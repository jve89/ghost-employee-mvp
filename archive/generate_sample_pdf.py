import fitz  # PyMuPDF

text = """
Invoice #391
Amount: €2,000
Please make payment before 10 June 2025.
"""

doc = fitz.open()
page = doc.new_page()
page.insert_text((72, 72), text)
doc.save("sample_inputs/sample_invoice.pdf")
print("✅ sample_invoice.pdf created")
