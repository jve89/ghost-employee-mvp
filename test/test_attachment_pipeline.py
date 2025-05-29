# test_attachment_pipeline.py

import os
from dotenv import load_dotenv
from src.inputs.attachment_processor import process_attachments
from src.processing.utils import group_tasks_by_source

load_dotenv()
print("🧪 Validating `source_file` field in extracted tasks...\n")

# Define your sample files
sample_files = [
    "sample_inputs/sample_notes.docx",
    "sample_inputs/sample_tasks.xlsx",
    "sample_inputs/sample_invoice.pdf",
]

all_tasks = []

for file_path in sample_files:
    print(f"\n🔍 Testing: {file_path}")
    tasks = process_attachments([file_path])
    all_tasks.extend(tasks)

    # Validation: ensure source_file is present
    missing_source = [t for t in tasks if "source_file" not in t or not t["source_file"]]
    if missing_source:
        print(f"❌ ERROR: Some tasks missing `source_file` in {file_path}")
    else:
        print(f"✅ All {len(tasks)} task(s) include 'source_file': {os.path.basename(file_path)}")

# ✅ Display grouped summary
print("\n📂 Grouped Task Overview:")
grouped = group_tasks_by_source(all_tasks)
for source, tasks in grouped.items():
    print(f"\n🗂️ Source: {source}")
    for i, task in enumerate(tasks, 1):
        print(f"  {i}. {task['description']}")
