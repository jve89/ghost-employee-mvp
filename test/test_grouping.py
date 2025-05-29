from src.processing.utils import group_tasks_by_source

sample_tasks = [
    {
        "title": "Pay invoice #123",
        "description": "Settle invoice #123 from supplier",
        "source_file": "sample_invoice.pdf"
    },
    {
        "title": "Review client feedback",
        "description": "Check feedback on project X",
        "source_file": "sample_notes.docx"
    },
    {
        "title": "Prepare budget draft",
        "description": "Draft Q3 budget proposal",
        "source_file": "manual"
    },
    {
        "title": "Update employee handbook",
        "description": "Include new remote work policies",
        "source_file": "sample_notes.docx"
    }
]

grouped = group_tasks_by_source(sample_tasks)

for source, tasks in grouped.items():
    print(f"\n📂 {source} ({len(tasks)} task{'s' if len(tasks) > 1 else ''})")
    for task in tasks:
        print(f" - {task['title']}")
