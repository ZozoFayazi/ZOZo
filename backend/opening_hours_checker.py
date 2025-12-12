"""
Opening Hours Checker for ZOZO Burger
Determines if a location is currently open based on opening_hours string
"""

from datetime import datetime, time
from typing import Tuple, Optional
import re

def parse_opening_hours(hours_str: str) -> dict:
    """
    Parse opening hours string like "11:00 - 22:45" or "Mo-So: 11:00-22:00"
    Returns dict with opening/closing times
    """
    # Remove spaces and common prefixes
    hours_str = hours_str.replace(" ", "").replace("Uhr", "").replace("Mo-So:", "").replace("Mo-Fr:", "")
    
    # Extract time range (HH:MM - HH:MM or HH:MM-HH:MM)
    match = re.search(r'(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})', hours_str)
    
    if match:
        open_hour, open_min, close_hour, close_min = map(int, match.groups())
        return {
            'open': time(open_hour, open_min),
            'close': time(close_hour, close_min)
        }
    
    # Default fallback
    return {
        'open': time(11, 0),
        'close': time(22, 45)
    }

def is_location_open(opening_hours: str, check_time: Optional[datetime] = None) -> Tuple[bool, str, Optional[str]]:
    """
    Check if location is currently open
    
    Args:
        opening_hours: Opening hours string from database
        check_time: Optional datetime to check (defaults to now)
    
    Returns:
        Tuple of (is_open: bool, status_text: str, next_opening: Optional[str])
    """
    if not check_time:
        check_time = datetime.now()
    
    current_time = check_time.time()
    current_day = check_time.weekday()  # 0 = Monday, 6 = Sunday
    
    # Parse hours
    hours = parse_opening_hours(opening_hours)
    open_time = hours['open']
    close_time = hours['close']
    
    # Check if currently open
    is_open = open_time <= current_time <= close_time
    
    if is_open:
        # Calculate minutes until closing
        closing_datetime = datetime.combine(check_time.date(), close_time)
        minutes_until_close = int((closing_datetime - check_time).total_seconds() / 60)
        
        if minutes_until_close < 30:
            status_text = f"Schließt bald (in {minutes_until_close} Min)"
            return True, status_text, None
        else:
            status_text = f"Jetzt geöffnet bis {close_time.strftime('%H:%M')}"
            return True, status_text, None
    else:
        # Location is closed
        if current_time < open_time:
            # Closed, but opens today
            status_text = "Geschlossen"
            next_opening = f"Öffnet heute um {open_time.strftime('%H:%M')}"
            return False, status_text, next_opening
        else:
            # Closed for today, opens tomorrow
            status_text = "Geschlossen"
            next_opening = f"Öffnet morgen um {open_time.strftime('%H:%M')}"
            return False, status_text, next_opening

def get_opening_status_for_location(location: dict) -> dict:
    """
    Get complete opening status for a location
    
    Args:
        location: Location dict with opening_hours field
    
    Returns:
        Dict with opening status info
    """
    opening_hours = location.get('opening_hours', '11:00 - 22:45')
    is_open, status_text, next_opening = is_location_open(opening_hours)
    
    return {
        'is_open': is_open,
        'status_text': status_text,
        'next_opening': next_opening,
        'opening_hours': opening_hours
    }
