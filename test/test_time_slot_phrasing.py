# /test_time_slot_phrasing.py

from src.processing.time_slot_parser import extract_time_slot
from dotenv import load_dotenv
import os

load_dotenv()

phrases = [
    "tomorrow morning",
    "next Monday at 3 PM",
    "Friday evening",
    "over twee weken om 10 uur",  # Dutch
    "volgende dinsdag om 14:30",  # Dutch
    "on 10 June",
    "end of next week",
    "later today",
    "early next month",
    "before lunch on Wednesday",
    "soon",  # Should probably fail
    "asap",  # Should return None
    "friday evening",
    "tomorrow morning",
    "later today",
    "early next month",
    "end of next week"
]

print("🕒 Time Slot Extraction Test Results:\n")
for phrase in phrases:
    result = extract_time_slot(phrase)
    print(f"{phrase.ljust(35)} → {result}")
