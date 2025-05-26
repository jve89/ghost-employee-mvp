import yaml
import os
import logging
import json
import time
import random
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from src.outputs import notion_exporter, sheets_exporter
from dotenv import load_dotenv
from datetime import datetime
import os
import boto3

load_dotenv()  # load .env variables into environment

s3_client = boto3.client('s3')  # boto3 reads AWS keys and region from env vars

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

CONFIG_PATH = "config.yaml"
RETRY_QUEUE_PATH = "retry_queue.json"
MAX_RETRIES = 5

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        CONFIG = yaml.safe_load(f)
else:
    CONFIG = {}

PRIORITY_ORDER = {"Low": 1, "Medium": 2, "High": 3}


def passes_filters(task: dict) -> bool:
    filters = CONFIG.get("export", {}).get("filters", {})
    min_priority = filters.get("min_priority", "Low")
    allowed_tags = filters.get("allowed_tags", [])
    excluded_users = filters.get("exclude_assigned_to", [])

    task_priority = task.get("priority", "Low")
    task_tags = task.get("tags", [])
    assigned_to = task.get("assigned_to", "")

    if PRIORITY_ORDER.get(task_priority, 1) < PRIORITY_ORDER.get(min_priority, 1):
        return False

    if allowed_tags and not any(tag in allowed_tags for tag in task_tags):
        return False

    if assigned_to in excluded_users:
        return False

    return True


def load_retry_queue():
    if os.path.exists(RETRY_QUEUE_PATH):
        with open(RETRY_QUEUE_PATH, "r") as f:
            try:
                return json.load(f)
            except Exception:
                logger.error("Failed to load retry queue, starting empty.")
                return []
    return []


def save_retry_queue(queue):
    with open(RETRY_QUEUE_PATH, "w") as f:
        json.dump(queue, f, indent=2)


def add_to_retry_queue(task, target):
    queue = load_retry_queue()
    queue.append({
        "task": task,
        "target": target,
        "attempts": 0,
        "last_attempt": None
    })
    save_retry_queue(queue)
    logger.warning(f"Added task to retry queue for target '{target}': {task.get('title', '[No Title]')}")


def export_to_s3(task, target):
    """
    Export the task data to an S3 bucket.
    The `target` format: s3://bucket-name/path/to/folder/
    """
    if s3_client is None:
        logger.error("S3 client not initialized.")
        return False

    try:
        # Parse bucket and key from target
        # Example target: s3://my-bucket/exports/
        target = target[len("s3://"):]
        parts = target.split("/", 1)
        bucket = parts[0]
        prefix = parts[1] if len(parts) > 1 else ""

        # Prepare the S3 object key
        file_name = task.get("file_name") or f"{task.get('title', 'export')}.json"
        if prefix and not prefix.endswith("/"):
            prefix += "/"
        s3_key = f"{prefix}{file_name}"

        # Serialize task payload to JSON bytes
        payload = task.get("payload", task)  # Expect payload in task or whole task as fallback
        data = json.dumps(payload).encode('utf-8')

        # Upload to S3
        s3_client.put_object(Bucket=bucket, Key=s3_key, Body=data)
        logger.info(f"Exported task '{task.get('title', '[No Title]')}' to s3://{bucket}/{s3_key}")
        return True

    except (BotoCoreError, ClientError) as e:
        logger.error(f"Failed to export to S3: {e}")
        return False


def export_to_target(task, target):
    logger.info(f"[DISPATCH] Routing task to export target: {target}")
    if target == "notion":
        return notion_exporter.export_to_notion(task)
    elif target in ("sheets", "google_sheets"): 
        return sheets_exporter.export_to_sheets(task)
    elif target.startswith("s3://"):
        return export_to_s3(task, target)
    else:
        logger.error(f"Unknown export target: {target}")
        return False


def export_to_targets(tasks, targets):
    results = []

    for task in tasks:
        for target in targets:
            try:
                success = export_to_target(task, target)
                results.append({
                    "task_id": task.get("id", task.get("title", "N/A")),
                    "target": target,
                    "status": "success" if success else "failed",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Exception while exporting task '{task.get('title', 'N/A')}' to {target}: {e}")
                results.append({
                    "task_id": task.get("id", task.get("title", "N/A")),
                    "target": target,
                    "status": "failed",
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e)
                })

    return results

def export_task(task: dict):
    enabled_targets = CONFIG.get("export", {}).get("enabled_targets", [])

    if not passes_filters(task):
        logger.info(f"Task did not pass export filters: {task.get('title', '[No Title]')}")
        return

    logger.info(f"Exporting task '{task.get('title', '[No Title]')}' to: {enabled_targets}")

    for target in enabled_targets:
        try:
            success = export_to_target(task, target)
            if success:
                logger.info(f"Task exported to {target} successfully.")
            else:
                logger.warning(f"Task export to {target} failed, queuing for retry.")
                add_to_retry_queue(task, target)
        except Exception as e:
            logger.error(f"Exception during export to {target}: {e}")
            add_to_retry_queue(task, target)
