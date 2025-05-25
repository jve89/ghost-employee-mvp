# /src/outputs/sheets_exporter.py

import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "service_account.json")  # fallback

def push_to_google_sheets(sheet_id, tasks, sheet_range="Sheet1!A1"):
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        values = [["Timestamp", "Title", "Description", "Due Date", "Assigned To", "Priority", "Time Slot"]]
        now = datetime.utcnow().isoformat()

        for task in tasks:
            values.append([
                now,
                task.get("title", ""),
                task.get("description", ""),
                task.get("due_date", ""),
                task.get("assigned_to", ""),
                task.get("priority", ""),
                task.get("time_slot", ""),
            ])

        body = {"values": values}

        try:
            result = sheet.values().update(
                spreadsheetId=sheet_id,
                range=sheet_range,
                valueInputOption="RAW",
                body=body,
            ).execute()
            print(f"[SHEETS] {result.get('updatedCells')} cells updated to {sheet_range}")

        except Exception as e:
            if sheet_range == "Sheet1!A1":
                print(f"[WARNING] Failed on Sheet1 — retrying with Blad1...")
                result = sheet.values().update(
                    spreadsheetId=sheet_id,
                    range="Blad1!A1",
                    valueInputOption="RAW",
                    body=body,
                ).execute()
                print(f"[SHEETS] {result.get('updatedCells')} cells updated to Blad1!A1")
            else:
                raise e

    except Exception as e:
        print(f"[ERROR] Failed to push to Google Sheets: {e}")

# Wrapper for single-task export, called by export_manager
def export_to_sheets(task):
    SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

    if not SHEET_ID:
        print("[SHEETS EXPORTER] ⚠️ GOOGLE_SHEET_ID not set in .env — skipping export.")
        return

    push_to_google_sheets(SHEET_ID, [task])

