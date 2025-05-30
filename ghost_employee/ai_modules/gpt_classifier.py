# /src/processing/gpt_classifier.py

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_task_with_gpt(text: str) -> dict:
    prompt = f"""
You are an assistant that extracts structured task data from text. Given the task description below, return JSON with:
- title
- description
- priority (High, Medium, Low)
- due_date (ISO format if any, else null)
- assigned_to (team or person name if mentioned)
- tags (list of keywords)

Task text:
\"\"\"
{text}
\"\"\"
Return JSON only.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        return eval(content)  # or use json.loads() if you wrap GPT output in code block
    except Exception as e:
        print(f"[GPT-CLASSIFIER] ❌ Failed: {e}")
        return {}
