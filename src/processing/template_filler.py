import os
from docxtpl import DocxTemplate
from datetime import datetime


def fill_template(template_path, context, output_dir="generated_docs"):
    os.makedirs(output_dir, exist_ok=True)

    try:
        doc = DocxTemplate(template_path)
        doc.render(context)

        timestamp = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
        output_filename = f"{output_dir}/filled_{timestamp}.docx"
        doc.save(output_filename)

        print(f"[DOC GENERATED] {output_filename}")
        return output_filename
    except Exception as e:
        print(f"[ERROR] Template filling failed: {e}")
        return None
