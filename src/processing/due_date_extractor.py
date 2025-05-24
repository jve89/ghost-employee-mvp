# src/processing/due_date_extractor.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_due_date(task_description):
    prompt = f"""
You are an assistant that extracts clear due dates from task descriptions.

Given:
\"\"\"{task_description}\"\"\"

Reply with only the date in YYYY-MM-DD format if a due date is implied or stated.
If no due date can be inferred, reply with "None".
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0
        )

        content = response.choices[0].message.content.strip()
        return content if content.lower() != "none" else None

    except Exception as e:
        print(f"[ERROR] Failed to extract due date: {e}")
        return None
