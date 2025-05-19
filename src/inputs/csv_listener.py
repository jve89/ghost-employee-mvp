import os
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

WATCHED_FOLDER = "watched"

class CSVHandler(FileSystemEventHandler):
    def process_csv(self, file_path):
        if not os.path.exists(file_path):
            print(f"[WARN] File no longer exists: {file_path}")
            return

        try:
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
            elif file_path.endswith(".xlsx"):
                df = pd.read_excel(file_path)
            else:
                print(f"[INFO] Unsupported file type: {file_path}")
                return

            print(f"[DATA LOADED] {file_path} - {len(df)} rows")
            print(df.head())  # Preview first few rows

            # TODO: Pass df to next module for rule evaluation

        except Exception as e:
            print(f"[ERROR] Failed to process {file_path}: {e}")

    def on_created(self, event):
        if not event.is_directory:
            print(f"[FILE CREATED] {event.src_path}")
            self.process_csv(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            print(f"[FILE MODIFIED] {event.src_path}")
            self.process_csv(event.src_path)

def start_csv_monitor():
    if not os.path.exists(WATCHED_FOLDER):
        os.makedirs(WATCHED_FOLDER)

    event_handler = CSVHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCHED_FOLDER, recursive=False)
    observer.start()
    print(f"[CSV MONITOR] Watching for .csv/.xlsx files in: {WATCHED_FOLDER}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_csv_monitor()
