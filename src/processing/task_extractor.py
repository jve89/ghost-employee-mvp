# /src/processing/task_extractor.py

from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from src.processing.due_date_extractor import extract_due_date
from src.processing.time_slot_parser import extract_time_slot
from src.processing.user_mapper import resolve_assigned_user

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_tasks(summary_text):
    """
    Extracts structured tasks from a given summary.
    Each task will be a dictionary with optional keys like 'description', 'due_date', 'priority', etc.
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
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.3,
        )

        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        tasks = json.loads(content)

        # Post-process each task to enrich data
        for task in tasks:
            if isinstance(task, dict) and "description" in task:
                if "due_date" not in task:
                    task["due_date"] = extract_due_date(task["description"])

                if "time_slot" not in task:
                    task["time_slot"] = extract_time_slot(task["description"])

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
