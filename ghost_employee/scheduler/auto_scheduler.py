import threading
import time

def start_background_jobs(interval: int = 1800):
    def job():
        while True:
            print("[Scheduler] Periodic job running (add logic here)")
            # TODO: Replace with real retry queue call
            time.sleep(interval)

    thread = threading.Thread(target=job, daemon=True)
    thread.start()
