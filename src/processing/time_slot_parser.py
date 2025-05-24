from dateparser import parse as parse_date
from datetime import datetime
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_time_slot(text):
    """
    Attempts to parse a time slot using dateparser, falls back to GPT if needed.
    Returns an ISO 8601 string or None.
    """
    dt = parse_date(text, settings={'PREFER_DATES_FROM': 'future'})
    if dt:
        return dt.isoformat()

    # GPT fallback
    try:
        prompt = f"""
Assume today's date is {datetime.now().date()}.

You are a smart scheduling assistant. Convert the following sentence into a single ISO 8601 datetime string.
Only return the date and time. Do NOT explain anything.

Text: \"{text}\"

Your answer should look like: 2025-06-05T15:00:00
"""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content.strip()

        # Optional: check if it's valid ISO format
        try:
            parsed_dt = datetime.fromisoformat(answer)
            return parsed_dt.isoformat()
        except ValueError:
            print(f"[GPT-TIMEPARSER] Response was not ISO format: {answer}")
            return answer  # Still return raw GPT guess

    except Exception as e:
        print(f"[GPT-TIMEPARSER ERROR] {e}")
        return None
