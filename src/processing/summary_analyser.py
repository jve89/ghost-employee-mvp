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
