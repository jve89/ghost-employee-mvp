# test_time_parser.py
from src.processing.time_slot_parser import extract_time_slot
from dotenv import load_dotenv
load_dotenv()

examples = [
    "Schedule a meeting next Thursday at 3 PM",
    "Book a call with the client tomorrow morning",
    "Let's meet on June 5th around 10:00",
    "Set up a review session Friday 14:30",
    "Plan a session for next Monday afternoon",
    "Meet me in 2 hours",
    "Catch up at 14:00 tomorrow",
    "Review call in 1 day at noon"
]

for example in examples:
    parsed = extract_time_slot(example)
    print(f"{example} → {parsed}")
