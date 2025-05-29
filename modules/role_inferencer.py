# role_inferencer.py

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ROLES = {
    "Finance Team": ["invoices", "payments", "budget", "expenses"],
    "HR Team": ["hiring", "onboarding", "employee", "salary", "leave"],
    "Vendor Assistant": ["suppliers", "vendors", "orders", "delivery", "procurement"]
}

def infer_role_from_description(task_text):
    try:
        prompt = f"""
You are an assistant that assigns business tasks to the correct internal team.

Here are the available teams and their focus areas:
{format_roles_for_prompt()}

Given the task below, return only the best matching team name (e.g., "Finance Team").

Task:
\"\"\"{task_text}\"\"\"
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )

        team = response.choices[0].message.content.strip()
        return team if team in ROLES else None

    except Exception as e:
        print(f"[ROLE INFER ERROR] {e}")
        return "General"

def format_roles_for_prompt():
    return "\n".join([f"- {role}: {', '.join(keywords)}" for role, keywords in ROLES.items()])
