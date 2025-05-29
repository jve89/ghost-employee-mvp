# test_due_date_phrasing.py

from src.processing.due_date_extractor import extract_due_date
from dotenv import load_dotenv
import os

load_dotenv()

TEST_CASES = {
    "volgende maandag": "Expected: parseable after normalisation",
    "komende vrijdag": "Expected: native Dutch parsing",
    "binnen twee weken": "Expected: relative phrasing",
    "eind Q2": "Expected: replaced with '30 juni'",
    "voor vrijdag": "Expected: natural phrasing",
    "op 10 juni": "Expected: direct date",
    "next Friday": "Expected: English phrasing",
    "by end of June": "Expected: English date phrasing",
    "before the deadline": "Too vague → fallback",
    "finalise the task in 3 days": "Relative time → fallback",
    "wrap up report before Tuesday": "Vague + relative → fallback",
    "make sure it's done quickly": "Too vague → should return None",
    "get it done soon": "Too vague → should return None",
    "urgently handle this task": "No date expected",
}

print("🔍 Due Date Extraction Test Results:\n")

for input_text, comment in TEST_CASES.items():
    result = extract_due_date(input_text)
    status = "✅" if result else "❌"
    print(f"{status} {input_text:<40} → {result}   ({comment})")
