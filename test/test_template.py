from src.processing.template_filler import fill_template

context = {
    "ClientName": "Johan",
    "Date": "2025-05-21"
}

fill_template("templates/sample_template.docx", context)
