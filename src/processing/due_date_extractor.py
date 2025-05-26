# /src/processing/due_date_extractor.py

import os
from dotenv import load_dotenv
from openai import OpenAI
import dateparser
import re

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_due_date(text):
    text = normalize_natural_phrasing(text)

    if not text:
        return None

    # Try local parsing first (Dutch and English)
    for lang in ['nl', 'en']:
        parsed = dateparser.parse(text, languages=[lang], settings={'PREFER_DATES_FROM': 'future'})
        if parsed:
            print(f"[DEBUG] Parsed locally '{text}' → {parsed.date().isoformat()}")
            return parsed.date().isoformat()

    # Fallback to GPT
    print(f"[FALLBACK] No local match for '{text}' → sending to GPT...")
    prompt = f"""
You are a smart assistant that extracts **a clear date** from ambiguous or casual time expressions.

Only return a single date in **YYYY-MM-DD** format.
If there is no date implied, respond with "None".

Examples:
- "next Friday" → "2025-05-30"
- "over twee weken" → "2025-06-08"
- "komende maandag" → "2025-06-02"
- "as soon as possible" → "None"

Input: \"\"\"{text}\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0
        )

        content = response.choices[0].message.content.strip()
        print(f"[RAW GPT OUTPUT] {content}")

        clean = content.strip().strip('"').strip("'")

        # Handle both real 'None' and GPT saying "None"
        if clean.lower() == "none":
            return None

        # Sanity check: valid ISO date format
        if re.match(r"^\d{4}-\d{2}-\d{2}$", clean):
            return clean

        print(f"[WARN] GPT returned unexpected format: {clean}")
        return None

    except Exception as e:
        print(f"[ERROR] Failed to extract due date via GPT fallback: {e}")
        return None

def normalize_natural_phrasing(text):
    substitutions = {
        "volgende maandag": "komende maandag",
        "volgende dinsdag": "komende dinsdag",
        "volgende woensdag": "komende woensdag",
        "volgende donderdag": "komende donderdag",
        "volgende vrijdag": "komende vrijdag",
        "volgende zaterdag": "komende zaterdag",
        "volgende zondag": "komende zondag",
        "eind Q1": "31 maart",
        "eind Q2": "30 juni",
        "eind Q3": "30 september",
        "eind Q4": "31 december",
        "binnen twee weken": "over twee weken",
        "voor vrijdag": "vóór vrijdag",
    }

    for original, replacement in substitutions.items():
        # Case-insensitive whole word replacement
        text = re.sub(rf"\b{re.escape(original)}\b", replacement, text, flags=re.IGNORECASE)

    return text

def recognise_due_dates(tasks):
    """
    Goes through a list of tasks and fills in the 'due_date' field
    by analysing each task's title + description.
    """
    for task in tasks:
        input_text = task.get("description", "") or task.get("title", "")
        due_date = extract_due_date(input_text)
        task["due_date"] = due_date
    return tasks
