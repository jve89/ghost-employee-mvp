# /src/processing/task_extractor.py

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from src.processing.due_date_extractor import extract_due_date
from src.processing.time_slot_parser import extract_time_slot
from src.processing.user_mapper import resolve_assigned_user
from src.processing.gpt_classifier import classify_task_with_gpt

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_tasks(summary_text):
    """
    Extracts structured tasks from a given summary using GPT,
    then enriches them with due dates, time slots, user resolution, etc.
    """

    prompt = f"""
You are an assistant that extracts clear, structured tasks from a summary.
Return them as a JSON list. Each task is a dictionary with at least:

- "description": a clear task
Optional keys (if available):
- "due_date": e.g. 2025-06-01
- "priority": e.g. High, Medium, Low
- "assigned_to": person or role
- "context": extra notes if useful

Summary:
\"\"\"{summary_text}\"\"\"

Respond ONLY with the JSON array.
Example output:

[
  {{
    "description": "Prepare Q2 financial report",
    "due_date": "2025-06-01",
    "priority": "High",
    "assigned_to": "Finance Team"
  }},
  {{
    "description": "Schedule Q2 review meeting",
    "context": "Include all department heads"
  }}
]
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.3,
        )

        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        tasks = json.loads(content)

        if not isinstance(tasks, list):
            raise ValueError("GPT response is not a list")

        if not tasks:
            print("[TASK EXTRACTOR] No structured tasks returned — using fallback GPT classifier...")
            fallback_task = classify_task_with_gpt(summary_text)
            if fallback_task:
                print("[TASK EXTRACTOR] ✅ Fallback succeeded.")
                return [fallback_task]
            else:
                print("[TASK EXTRACTOR] ❌ Fallback also failed.")
                return []

        # Post-process each task
        for task in tasks:
            if not isinstance(task, dict) or "description" not in task:
                continue

            if "due_date" not in task:
                task["due_date"] = extract_due_date(task["description"])

            if "time_slot" not in task:
                slot = extract_time_slot(task["description"])
                if isinstance(slot, dict):
                    task["time_slot"] = slot.get("datetime")
                    task["time_slot_source"] = slot.get("source")
                    task["time_slot_confidence"] = slot.get("confidence")
                else:
                    task["time_slot"] = slot

            if "assigned_to" in task:
                task["assigned_user"] = resolve_assigned_user(task["assigned_to"])

        print(f"[TASK EXTRACTOR] Extracted {len(tasks)} task(s).")
        return tasks

    except json.JSONDecodeError:
        print("[TASK EXTRACTOR] Failed to parse GPT response as JSON.")
        print("Raw output:", content)
        return []

    except Exception as e:
        print(f"[ERROR] Failed to extract tasks: {e}")
        return []
