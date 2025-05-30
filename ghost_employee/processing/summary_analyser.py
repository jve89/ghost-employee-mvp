from openai import OpenAI
import os
from src.processing.task_extractor import extract_tasks  # ✅ Import from your task extractor module

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyse_summary(summary_text):
    """
    Checks the summary text for trigger phrases.
    Returns a list of trigger alerts (if any).
    """
    triggers = {
        "cancel": "⚠️ Project at risk of cancellation",
        "frustrated": "⚠️ Client frustration detected",
        "missed appointment": "⚠️ Missed meeting/appointment"
    }

    alerts = []
    lowered = summary_text.lower()

    for phrase, message in triggers.items():
        if phrase in lowered:
            alerts.append(message)

    return alerts

def summarise_file(filepath):
    """
    Sends file content to GPT-4o via OpenAI SDK v1.x and returns the summary and tasks.
    """
    with open(filepath, "r") as f:
        content = f.read()

    print(f"[INFO] Sending content of {filepath} to GPT...")

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Summarise the following content and extract action items."},
                {"role": "user", "content": content}
            ]
        )
        summary = response.choices[0].message.content.strip()
        print(f"\n[SUMMARY for {filepath}]\n{summary}\n{'=' * 60}")

        tasks = extract_tasks(summary)
        return summary, tasks

    except Exception as e:
        print(f"[ERROR] GPT failed to summarise: {e}")
        return "Failed to generate summary.", []

def tag_summary(summary_text: str) -> tuple[str, str]:
    tags = {
        "contract": ("💼", ["contract", "agreement", "signed", "terms"]),
        "invoice": ("💰", ["invoice", "payment due", "billing", "amount"]),
        "reminder": ("⏰", ["reminder", "follow up", "due", "deadline"]),
        "report": ("📊", ["report", "summary", "overview", "analysis"]),
        "hr": ("👥", ["onboarding", "employee", "training", "benefits"])
    }
    summary_text_lower = summary_text.lower()
    for tag, (icon, keywords) in tags.items():
        if any(kw in summary_text_lower for kw in keywords):
            return tag, icon
    return "uncategorised", "📁"
