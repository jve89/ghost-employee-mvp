# /src/inputs/archiver.py

import os
import shutil
from datetime import datetime

ARCHIVE_DIR = "archived_attachments"

def archive_attachment(filepath):
    """Moves the file to an archive folder with a timestamped name."""
    if not os.path.exists(filepath):
        print(f"[ARCHIVER] File not found: {filepath}")
        return

    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(filepath)
    new_name = f"{timestamp}_{filename}"
    dest = os.path.join(ARCHIVE_DIR, new_name)

    try:
        shutil.move(filepath, dest)
        print(f"[ARCHIVER] Archived {filename} → {new_name}")
    except Exception as e:
        print(f"[ARCHIVER ERROR] Failed to archive {filename}: {e}")
