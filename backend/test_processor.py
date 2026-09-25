from app.services.document_processor import extract_text_from_pdf


file_path = "uploads/resume1.pdf"

text = extract_text_from_pdf(file_path)

print("Extracted characters:", len(text))
print()
print(text[:2000])