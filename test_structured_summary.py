# test_structured_summary.py

from src.processing.structured_saver import save_structured_summary

summary_text = "This is a finance-related weekly meeting summary with updates on the Q2 report."
tasks = ["Prepare Q2 report", "Send invoice to client"]
alerts = ["Delayed submission by finance team"]
attachments = ["invoice_q2.pdf", "report_draft.docx"]
email_subject = "Weekly Finance Sync"
email_from = "johan@example.com"

save_structured_summary(
    summary_data=summary_text,
    tasks=tasks,
    alerts=alerts,
    attachments=attachments,
    email_subject=email_subject,
    email_from=email_from
)
