from io import BytesIO

import fitz
from docx import Document


def extract_pdf_text(file_bytes: bytes) -> str:
    document = fitz.open(stream=file_bytes, filetype="pdf")

    pages = []

    for page in document:
        pages.append(page.get_text("text"))

    document.close()

    return "\n".join(pages).strip()


def extract_docx_text(file_bytes: bytes) -> str:
    document = Document(BytesIO(file_bytes))

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    return "\n".join(paragraphs).strip()


def extract_txt_text(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8").strip()
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1").strip()


def extract_document_text(uploaded_file) -> str:
    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()

    if file_name.endswith(".pdf"):
        return extract_pdf_text(file_bytes)

    if file_name.endswith(".docx"):
        return extract_docx_text(file_bytes)

    if file_name.endswith(".txt"):
        return extract_txt_text(file_bytes)

    raise ValueError("Unsupported file type.")