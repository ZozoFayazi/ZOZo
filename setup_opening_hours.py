#!/usr/bin/env python3
"""
Setup Opening Hours for both locations
"""
import os
from pymongo import MongoClient
from datetime import datetime, timedelta

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(mongo_url)
db = client['zozo_burger']

print("🕐 Setting up Opening Hours...")
print("="*60)

# Standard weekly schedule
standard_schedule = [
    {
        "day": "monday",
        "is_open": True,
        "time_slots": [
            {"start": "11:00", "end": "14:30"},
            {"start": "17:00", "end": "22:30"}
        ]
    },
    {
        "day": "tuesday",
        "is_open": True,
        "time_slots": [
            {"start": "11:00", "end": "14:30"},
            {"start": "17:00", "end": "22:30"}
        ]
    },
    {
        "day": "wednesday",
        "is_open": True,
        "time_slots": [
            {"start": "11:00", "end": "14:30"},
            {"start": "17:00", "end": "22:30"}
        ]
    },
    {
        "day": "thursday",
        "is_open": True,
        "time_slots": [
            {"start": "11:00", "end": "14:30"},
            {"start": "17:00", "end": "22:30"}
        ]
    },
    {
        "day": "friday",
        "is_open": True,
        "time_slots": [
            {"start": "11:00", "end": "14:30"},
            {"start": "17:00", "end": "23:00"}
        ]
    },
    {
        "day": "saturday",
        "is_open": True,
        "time_slots": [
            {"start": "12:00", "end": "23:00"}
        ]
    },
    {
        "day": "sunday",
        "is_open": True,
        "time_slots": [
            {"start": "12:00", "end": "22:00"}
        ]
    }
]

# Special days (Feiertage)
# Calculate next few special days
tomorrow = (datetime.now() + timedelta(days=1)).date()
day_after = (datetime.now() + timedelta(days=2)).date()
in_5_days = (datetime.now() + timedelta(days=5)).date()

special_days = [
    {
        "date": tomorrow.isoformat(),
        "is_open": False,
        "time_slots": [],
        "note": "Test: Morgen geschlossen",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "date": day_after.isoformat(),
        "is_open": True,
        "time_slots": [
            {"start": "14:00", "end": "20:00"}
        ],
        "note": "Test: Spezielle Zeiten",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]

# Update both locations
for slug in ["rellingen", "henstedt-ulzburg"]:
    result = db.locations.update_one(
        {"slug": slug},
        {
            "$set": {
                "opening_hours": standard_schedule,
                "special_opening_days": special_days,
                "timezone": "Europe/Berlin",
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count > 0:
        print(f"✅ {slug}: Opening hours configured")
        print(f"   Weekly: {len(standard_schedule)} days")
        print(f"   Special: {len(special_days)} days")
    else:
        print(f"❌ {slug}: Location not found")

print("\n✅ Opening hours setup complete!")
print("="*60)
