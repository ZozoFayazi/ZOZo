"""
Opening Hours Management Service
Handles standard weekly schedules + special day overrides
"""
from datetime import datetime, date, time, timedelta, timezone
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class OpeningHoursService:
    """Service for managing opening hours with override support"""
    
    def __init__(self, db):
        self.db = db
    
    def _parse_time(self, time_str: str) -> time:
        """Parse time string HH:MM to time object"""
        try:
            hours, minutes = map(int, time_str.split(':'))
            return time(hour=hours, minute=minutes)
        except:
            return None
    
    def _is_time_in_range(self, check_time: time, start: time, end: time) -> bool:
        """Check if time is within range (handles overnight ranges)"""
        if start <= end:
            return start <= check_time <= end
        else:
            # Overnight range (e.g., 22:00 - 02:00)
            return check_time >= start or check_time <= end
    
    async def get_opening_hours(self, location_slug: str) -> Dict:
        """Get complete opening hours for a location"""
        location = await self.db.locations.find_one({"slug": location_slug})
        if not location:
            return None
        
        return {
            "location_slug": location_slug,
            "location_name": location.get("name"),
            "weekly_schedule": location.get("opening_hours", []),
            "special_days": location.get("special_opening_days", []),
            "timezone": location.get("timezone", "Europe/Berlin")
        }
    
    async def update_weekly_schedule(
        self, 
        location_slug: str, 
        weekly_schedule: List[Dict]
    ) -> bool:
        """
        Update standard weekly schedule
        
        weekly_schedule format:
        [
            {
                "day": "monday",
                "is_open": true,
                "time_slots": [
                    {"start": "11:00", "end": "14:00"},
                    {"start": "17:00", "end": "22:00"}
                ]
            },
            ...
        ]
        """
        try:
            result = await self.db.locations.update_one(
                {"slug": location_slug},
                {
                    "$set": {
                        "opening_hours": weekly_schedule,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            return result.matched_count > 0
        except Exception as e:
            logger.error(f"Update weekly schedule error: {str(e)}")
            return False
    
    async def add_special_day(
        self, 
        location_slug: str, 
        date_str: str,  # YYYY-MM-DD
        is_open: bool,
        time_slots: List[Dict] = None,
        note: str = None
    ) -> Dict:
        """
        Add or update a special day override
        
        Args:
            date_str: Date in YYYY-MM-DD format
            is_open: True if open, False if closed
            time_slots: List of {"start": "HH:MM", "end": "HH:MM"} if open
            note: Optional note (e.g., "Weihnachten", "Betriebsfeier")
        """
        try:
            special_day = {
                "date": date_str,
                "is_open": is_open,
                "time_slots": time_slots or [],
                "note": note or "",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Remove existing entry for this date
            await self.db.locations.update_one(
                {"slug": location_slug},
                {
                    "$pull": {"special_opening_days": {"date": date_str}}
                }
            )
            
            # Add new entry
            result = await self.db.locations.update_one(
                {"slug": location_slug},
                {
                    "$push": {"special_opening_days": special_day},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
            )
            
            return {
                "success": result.matched_count > 0,
                "special_day": special_day
            }
        except Exception as e:
            logger.error(f"Add special day error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def delete_special_day(self, location_slug: str, date_str: str) -> bool:
        """Delete a special day override"""
        try:
            result = await self.db.locations.update_one(
                {"slug": location_slug},
                {
                    "$pull": {"special_opening_days": {"date": date_str}},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
            )
            return result.matched_count > 0
        except Exception as e:
            logger.error(f"Delete special day error: {str(e)}")
            return False
    
    async def check_is_open_now(
        self, 
        location_slug: str,
        check_datetime: datetime = None
    ) -> Dict:
        """
        Check if location is currently open
        
        Returns:
            {
                "is_open": bool,
                "current_slot": {"start": "11:00", "end": "22:00"} or None,
                "next_opening": datetime or None,
                "reason": str (e.g., "Heute geschlossen", "Außerhalb Öffnungszeiten")
            }
        """
        if check_datetime is None:
            check_datetime = datetime.now(timezone.utc)
        
        location = await self.db.locations.find_one({"slug": location_slug})
        if not location:
            return {"is_open": False, "reason": "Location not found"}
        
        # Get timezone (default: Europe/Berlin)
        tz_str = location.get("timezone", "Europe/Berlin")
        try:
            import pytz
            tz = pytz.timezone(tz_str)
            local_time = check_datetime.astimezone(tz)
        except:
            # Fallback if pytz not available
            local_time = check_datetime
        
        check_date = local_time.date()
        check_time = local_time.time()
        date_str = check_date.isoformat()
        day_name = check_date.strftime("%A").lower()
        
        # 1. Check for special day override (has priority!)
        special_days = location.get("special_opening_days", [])
        special_day = next((d for d in special_days if d["date"] == date_str), None)
        
        if special_day:
            if not special_day["is_open"]:
                return {
                    "is_open": False,
                    "reason": f"Sondertag: {special_day.get('note', 'Geschlossen')}",
                    "current_slot": None,
                    "next_opening": await self._find_next_opening(location, check_datetime)
                }
            
            # Check special day time slots
            for slot in special_day.get("time_slots", []):
                start = self._parse_time(slot["start"])
                end = self._parse_time(slot["end"])
                if start and end and self._is_time_in_range(check_time, start, end):
                    return {
                        "is_open": True,
                        "current_slot": slot,
                        "reason": f"Sondertag: {special_day.get('note', 'Geöffnet')}"
                    }
            
            # Special day but outside time slots
            return {
                "is_open": False,
                "reason": f"Sondertag außerhalb der Öffnungszeiten",
                "current_slot": None,
                "next_opening": await self._find_next_opening(location, check_datetime)
            }
        
        # 2. Check weekly schedule
        weekly_schedule = location.get("opening_hours", [])
        
        # Handle both formats: list of objects or string
        if isinstance(weekly_schedule, str):
            # Simple string format "11:00 - 22:00"
            start = self._parse_time(weekly_schedule.split('-')[0].strip())
            end = self._parse_time(weekly_schedule.split('-')[1].strip())
            if start and end and self._is_time_in_range(check_time, start, end):
                return {
                    "is_open": True,
                    "current_slot": {"start": weekly_schedule.split('-')[0].strip(), "end": weekly_schedule.split('-')[1].strip()},
                    "reason": "Reguläre Öffnungszeiten"
                }
        
        elif isinstance(weekly_schedule, list):
            # Structured format
            day_schedule = next((d for d in weekly_schedule if d.get("day", "").lower() == day_name), None)
            
            if not day_schedule or not day_schedule.get("is_open", True):
                return {
                    "is_open": False,
                    "reason": "Heute geschlossen",
                    "current_slot": None,
                    "next_opening": await self._find_next_opening(location, check_datetime)
                }
            
            # Check time slots
            time_slots = day_schedule.get("time_slots", [])
            if not time_slots:
                # Fallback to old format (open_time/close_time)
                open_time = day_schedule.get("open_time")
                close_time = day_schedule.get("close_time")
                if open_time and close_time:
                    time_slots = [{"start": open_time, "end": close_time}]
            
            for slot in time_slots:
                start = self._parse_time(slot["start"])
                end = self._parse_time(slot["end"])
                if start and end and self._is_time_in_range(check_time, start, end):
                    return {
                        "is_open": True,
                        "current_slot": slot,
                        "reason": "Reguläre Öffnungszeiten"
                    }
        
        # Not in any time slot
        return {
            "is_open": False,
            "reason": "Außerhalb der Öffnungszeiten",
            "current_slot": None,
            "next_opening": await self._find_next_opening(location, check_datetime)
        }
    
    async def _find_next_opening(
        self, 
        location: Dict, 
        from_datetime: datetime
    ) -> Optional[datetime]:
        """Find next opening time"""
        try:
            # Simple implementation: check next 7 days
            for days_ahead in range(1, 8):
                check_date = (from_datetime + timedelta(days=days_ahead)).date()
                date_str = check_date.isoformat()
                day_name = check_date.strftime("%A").lower()
                
                # Check special days first
                special_days = location.get("special_opening_days", [])
                special_day = next((d for d in special_days if d["date"] == date_str), None)
                
                if special_day and special_day["is_open"] and special_day.get("time_slots"):
                    first_slot = special_day["time_slots"][0]
                    start_time = self._parse_time(first_slot["start"])
                    if start_time:
                        return datetime.combine(check_date, start_time)
                elif special_day and not special_day["is_open"]:
                    continue  # Skip closed special days
                
                # Check weekly schedule
                weekly_schedule = location.get("opening_hours", [])
                if isinstance(weekly_schedule, list):
                    day_schedule = next((d for d in weekly_schedule if d.get("day", "").lower() == day_name), None)
                    
                    if day_schedule and day_schedule.get("is_open", True):
                        time_slots = day_schedule.get("time_slots", [])
                        if time_slots:
                            first_slot = time_slots[0]
                            start_time = self._parse_time(first_slot["start"])
                            if start_time:
                                return datetime.combine(check_date, start_time)
            
            return None
        except Exception as e:
            logger.error(f"Find next opening error: {str(e)}")
            return None
    
    async def get_available_time_slots(
        self,
        location_slug: str,
        target_date: date,
        slot_duration_minutes: int = 15
    ) -> List[Dict]:
        """
        Get available delivery/pickup time slots for a specific date
        
        Returns list of time slots:
        [
            {"start": "11:00", "end": "11:15", "available": true},
            ...
        ]
        """
        try:
            location = await self.db.locations.find_one({"slug": location_slug})
            if not location:
                return []
            
            date_str = target_date.isoformat()
            day_name = target_date.strftime("%A").lower()
            
            # Check for special day
            special_days = location.get("special_opening_days", [])
            special_day = next((d for d in special_days if d["date"] == date_str), None)
            
            opening_slots = []
            
            if special_day:
                if not special_day["is_open"]:
                    return []  # Closed on this special day
                opening_slots = special_day.get("time_slots", [])
            else:
                # Use weekly schedule
                weekly_schedule = location.get("opening_hours", [])
                if isinstance(weekly_schedule, list):
                    day_schedule = next((d for d in weekly_schedule if d.get("day", "").lower() == day_name), None)
                    if day_schedule and day_schedule.get("is_open", True):
                        opening_slots = day_schedule.get("time_slots", [])
            
            # Generate time slots
            available_slots = []
            for slot in opening_slots:
                start_time = self._parse_time(slot["start"])
                end_time = self._parse_time(slot["end"])
                
                if not start_time or not end_time:
                    continue
                
                current = datetime.combine(target_date, start_time)
                end = datetime.combine(target_date, end_time)
                
                while current < end:
                    slot_end = current + timedelta(minutes=slot_duration_minutes)
                    if slot_end <= end:
                        available_slots.append({
                            "start": current.strftime("%H:%M"),
                            "end": slot_end.strftime("%H:%M"),
                            "available": True
                        })
                    current = slot_end
            
            return available_slots
        
        except Exception as e:
            logger.error(f"Get available slots error: {str(e)}")
            return []
