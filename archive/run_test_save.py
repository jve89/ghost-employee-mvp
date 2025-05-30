# run_test_save.py

from src.processing.structured_saver import save_structured_summary

save_structured_summary(
    summary_data="Tasks for newsletter",
    tasks=[],
    alerts=[],
    attachments=[
        "sample_inputs/sample_notes.docx",
        "sample_inputs/sample_tasks.xlsx",
        "sample_inputs/sample_invoice.pdf"
    ],
    email_subject="Test email import",
    email_from="manager@example.com"
)
