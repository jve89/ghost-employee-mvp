import pandas as pd

def analyse_csv(file_path):
    try:
        df = pd.read_csv(file_path)

        alerts = []

        # Check for delayed statuses
        if 'Status' in df.columns:
            issues = df[df['Status'].str.lower() == 'delayed']
            if not issues.empty:
                alerts.append(f"⚠️ {len(issues)} delayed items found in 'Status' column.")

        # Check for negative client sentiment
        if 'Client Sentiment' in df.columns:
            negative_sentiments = ['angry', 'unhappy', 'frustrated']
            negative = df[df['Client Sentiment'].str.lower().isin(negative_sentiments)]
            if not negative.empty:
                alerts.append(f"⚠️ {len(negative)} unhappy clients detected.")

        return alerts

    except Exception as e:
        print(f"[ERROR] Failed to analyse CSV: {e}")
        return []
