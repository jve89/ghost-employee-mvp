import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LOGS_FOLDER = "logs"

class LogEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".txt"):
            print(f"\n📥 [DASHBOARD] New log file detected: {event.src_path}\n")
            try:
                with open(event.src_path, "r") as f:
                    content = f.read()
                print("📄 [SUMMARY CONTENT]:\n")
                print(content)
                print("\n" + "="*60 + "\n")
            except Exception as e:
                print(f"[ERROR] Could not read log file: {e}")

def start_dashboard_viewer():
    if not os.path.exists(LOGS_FOLDER):
        os.makedirs(LOGS_FOLDER)

    event_handler = LogEventHandler()
    observer = Observer()
    observer.schedule(event_handler, LOGS_FOLDER, recursive=False)
    observer.start()
    print(f"[DASHBOARD STARTED] Monitoring log folder: {LOGS_FOLDER}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_dashboard_viewer()
