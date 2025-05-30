import json
import os
import time
import random
import logging
from pathlib import Path
from queue_utils import load_retry_queue, save_retry_queue
from src.outputs import export_manager
from logstore.history_logger import log_export_result

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

RETRY_QUEUE_PATH = "retry_queue.json"
MAX_RETRIES = 5
BASE_DELAY = 5  # seconds
MAX_DELAY = 300  # seconds (5 minutes)

# --- Dead-letter queue support ---
DEAD_LETTER_PATH = "dead_tasks.json"

def load_dead_tasks():
    if Path(DEAD_LETTER_PATH).exists():
        with open(DEAD_LETTER_PATH, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_dead_tasks(tasks):
    with open(DEAD_LETTER_PATH, "w") as f:
        json.dump(tasks, f, indent=2)

def exponential_backoff(attempt):
    delay = min(BASE_DELAY * (2 ** (attempt - 1)), MAX_DELAY)
    jitter = random.uniform(0, delay * 0.2)
    return delay + jitter

def handle_retries(queue_path, tasks, export_results):
    """
    Appends failed tasks to the retry queue based on export_results.
    """
    try:
        with open(queue_path, "r") as f:
            queue = json.load(f)
    except Exception:
        queue = []

    for task, result in zip(tasks, export_results):
        if result.get("status") != "success":
            queue.append({
                "task": task,
                "target": result.get("target"),
                "attempts": 0,
                "last_attempt": None,
                "retry_result": False,
                "result_timestamp": None
            })

    try:
        with open(queue_path, "w") as f:
            json.dump(queue, f, indent=2)
        print(f"[RETRY] Appended {len(queue)} task(s) to {queue_path}")
    except Exception as e:
        print(f"[RETRY ERROR] Failed to update retry queue: {e}")

def retry_worker():
    while True:
        queue = load_retry_queue()
        new_queue = []

        for entry in queue:
            task = entry["task"]
            target = entry["target"]
            attempts = entry.get("attempts", 0) + 1

            logger.info(f"Retrying task '{task.get('title', '[No Title]')}' to {target}, attempt {attempts}")

            success = False
            try:
                success = export_manager.export_to_target(task, target)
            except Exception as e:
                logger.error(f"Exception during retry export: {e}")
                success = False

            entry["attempts"] = attempts
            entry["last_attempt"] = time.time()
            entry["result_timestamp"] = time.time()
            entry["retry_result"] = success

            if success:
                logger.info(f"Retry succeeded for task '{task.get('title', '[No Title]')}' to {target}")
                log_export_result(
                    task_id=task.get("id", "unknown"),
                    title=task.get("title", "[No Title]"),
                    target=target,
                    status="success",
                    attempts=attempts
                )
                continue

            elif attempts >= MAX_RETRIES:
                logger.warning(f"Task '{task.get('title', '[No Title]')}' moved to dead-letter queue after {attempts} failed attempts.")
                log_export_result(
                    task_id=task.get("id", "unknown"),
                    title=task.get("title", "[No Title]"),
                    target=target,
                    status="failure",
                    attempts=attempts,
                    message="Max retries reached"
                )
                dead_tasks = load_dead_tasks()
                dead_tasks.append(entry)
                save_dead_tasks(dead_tasks)
                continue

            
            else:
                delay = exponential_backoff(attempts)
                logger.info(f"Waiting {delay:.1f}s before next retry for task '{task.get('title', '[No Title]')}'")
                new_queue.append(entry)
                time.sleep(delay)

        save_retry_queue(new_queue)

        if not new_queue:
            logger.info("Retry queue empty, sleeping 30s")
            time.sleep(30)

if __name__ == "__main__":
    logger.info("Starting retry worker...")
    retry_worker()
