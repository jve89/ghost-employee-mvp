import os
import docx
import pandas as pd

def extract_text_from_pdf(file_path):
    try:
        import fitz  # PyMuPDF
        text = ""
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text()
        if len(text.strip()) >= 30:
            return text.strip()
    except Exception as e:
        print(f"[WARN] PyMuPDF failed on {file_path}: {e}")

    # Fallback: pdfplumber
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        print(f"[ERROR] pdfplumber also failed: {e}")
        return None


def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"[ERROR] Failed to parse DOCX: {e}")
        return None


def extract_tasks_from_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        tasks = []
        for _, row in df.iterrows():
            task = {
                "description": row.get("Action", "").strip(),
                "due_date": str(row.get("Deadline", "")).strip(),
                "priority": row.get("Priority", "").strip(),
                "assigned_to": row.get("Assigned To", "").strip(),
            }
            if task["description"]:
                tasks.append(task)
        return tasks
    except Exception as e:
        print(f"[ERROR] Failed to parse Excel file: {e}")
        return []


def parse_attachment(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext in [".xlsx", ".xls"]:
        return extract_tasks_from_excel(file_path)
    else:
        print(f"[SKIPPED] Unsupported file type: {file_path}")
        return None
