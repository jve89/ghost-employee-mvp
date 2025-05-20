from openai import OpenAI
import os

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
    Sends file content to GPT-4o via OpenAI SDK v1.x and returns the summary.
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
        return summary

    except Exception as e:
        print(f"[ERROR] GPT failed to summarise: {e}")
        return "Failed to generate summary."
