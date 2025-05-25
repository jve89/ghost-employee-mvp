# /src/processing/time_slot_parser.py

from dateparser import parse as parse_date
from datetime import datetime, timedelta
from openai import OpenAI
import os
import re
import pytz

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEFAULT_TIME = "09:00:00"
LOCAL_TZ = pytz.timezone(os.getenv("LOCAL_TIMEZONE", "Europe/Amsterdam"))


def extract_time_slot(text, priority=None):
    """
    Attempts to parse a time slot using dateparser, falls back to GPT if needed.
    Returns a dict: {"datetime": ISO string, "source": "local" | "gpt" | "default", "confidence": "high" | "medium" | "low"}
    """
    text = normalize_time_phrasing(text)

    dt = parse_date(text, settings={
        'PREFER_DATES_FROM': 'future',
        'TIMEZONE': str(LOCAL_TZ),
        'RETURN_AS_TIMEZONE_AWARE': True
    })
    if dt:
        return {
            "datetime": dt.isoformat(),
            "source": "local",
            "confidence": "high"
        }

    # Handle vague expressions manually
    if text.lower().strip() in ["asap", "soon", "later today"]:
        now = datetime.now(LOCAL_TZ)
        suggested_time = now + timedelta(hours=4)
        fallback = suggested_time.replace(minute=0, second=0, microsecond=0)
        return {
            "datetime": fallback.isoformat(),
            "source": "default",
            "confidence": "low"
        }

    # Fallback to GPT
    try:
        prompt = f"""
Assume today's date is {datetime.now().date()}.

You are a smart scheduling assistant. Convert the following sentence into a single ISO 8601 datetime string.
Only return the date and time. Do NOT explain anything.

Text: "{text}"

Your answer should look like: 2025-06-05T15:00:00
"""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content.strip()

        try:
            parsed_dt = datetime.fromisoformat(answer)
            parsed_dt = LOCAL_TZ.localize(parsed_dt) if parsed_dt.tzinfo is None else parsed_dt
            return {
                "datetime": parsed_dt.isoformat(),
                "source": "gpt",
                "confidence": "medium"
            }
        except ValueError:
            print(f"[GPT-TIMEPARSER] Response was not ISO format: {answer}")
            return {
                "datetime": answer,
                "source": "gpt",
                "confidence": "low"
            }

    except Exception as e:
        print(f"[GPT-TIMEPARSER ERROR] {e}")
        return None


def normalize_time_phrasing(text):
    substitutions = {
        r"\bend of next week\b": f"on {(datetime.now() + timedelta(days=(12 - datetime.now().weekday()))).strftime('%Y-%m-%d')} at 23:59:59",
        r"\bearly next month\b": f"on {(datetime.now().replace(day=1) + timedelta(days=35)).replace(day=5).strftime('%Y-%m-%d')} at 15:00:00",
        r"\blater today\b": f"on {datetime.now().strftime('%Y-%m-%d')} at 15:00:00",
        r"\bbefore lunch on (\w+)\b": r"on \1 at 11:00",
        r"\bfriday evening\b": "on Friday at 18:00",
        r"\btomorrow morning\b": f"on {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')} at 08:00:00",
        r"\basap\b": "as soon as possible",
        r"\bsoon\b": "soon"
    }
    for pattern, repl in substitutions.items():
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text
