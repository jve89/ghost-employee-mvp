import json
import time
import random
import logging
from src.outputs import export_manager

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


def load_retry_queue():
    try:
        with open(RETRY_QUEUE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        logger.error("Failed to load retry queue, starting empty.")
        return []


def save_retry_queue(queue):
    with open(RETRY_QUEUE_PATH, "w") as f:
        json.dump(queue, f, indent=2)


def exponential_backoff(attempt):
    delay = min(BASE_DELAY * (2 ** (attempt - 1)), MAX_DELAY)
    jitter = random.uniform(0, delay * 0.2)
    return delay + jitter


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

            if success:
                logger.info(f"Retry succeeded for task '{task.get('title', '[No Title]')}' to {target}")
            elif attempts >= MAX_RETRIES:
                logger.error(f"Max retries reached for task '{task.get('title', '[No Title]')}' to {target}. Giving up.")
                # Could add alerting here or move to a dead-letter queue
            else:
                entry["attempts"] = attempts
                entry["last_attempt"] = time.time()
                new_queue.append(entry)
                delay = exponential_backoff(attempts)
                logger.info(f"Waiting {delay:.1f}s before next retry for task '{task.get('title', '[No Title]')}'")
                time.sleep(delay)

        save_retry_queue(new_queue)
        if not new_queue:
            logger.info("Retry queue empty, sleeping 30s")
            time.sleep(30)


if __name__ == "__main__":
    logger.info("Starting retry worker...")
    retry_worker()
