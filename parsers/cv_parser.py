from pathlib import Path
from typing import BinaryIO

import fitz
from docx import Document

from services.ocr_service import (
    OCRError,
    extract_text_from_pdf_with_ocr,
)


MIN_DIRECT_PDF_TEXT_LENGTH = 80


def read_uploaded_file_bytes(
    uploaded_file,
) -> bytes:
    """
    Read uploaded file bytes safely.
    """

    if hasattr(
        uploaded_file,
        "getvalue",
    ):
        return uploaded_file.getvalue()

    if hasattr(
        uploaded_file,
        "read",
    ):
        file_bytes = uploaded_file.read()

        try:
            uploaded_file.seek(
                0
            )
        except Exception:
            pass

        return file_bytes

    raise ValueError(
        "The uploaded file could not be read."
    )


def extract_text_from_pdf_bytes(
    pdf_bytes: bytes,
) -> str:
    """
    Extract selectable text from a PDF.
    """

    if not pdf_bytes:
        return ""

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf",
    )

    try:
        page_texts = []

        for page in document:
            page_texts.append(
                page.get_text(
                    "text"
                )
            )

        return "\n".join(
            page_texts
        ).strip()

    finally:
        document.close()


def extract_text_from_docx_bytes(
    docx_bytes: bytes,
) -> str:
    """
    Extract text from a DOCX file.
    """

    from io import BytesIO

    document = Document(
        BytesIO(
            docx_bytes
        )
    )

    paragraphs = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    table_text = []

    for table in document.tables:
        for row in table.rows:
            values = [
                cell.text.strip()
                for cell in row.cells
                if cell.text.strip()
            ]

            if values:
                table_text.append(
                    " | ".join(
                        values
                    )
                )

    return "\n".join(
        paragraphs
        + table_text
    ).strip()


def extract_text_from_txt_bytes(
    text_bytes: bytes,
) -> str:
    """
    Decode a TXT file.
    """

    for encoding in [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin-1",
    ]:
        try:
            return text_bytes.decode(
                encoding
            ).strip()

        except UnicodeDecodeError:
            continue

    return text_bytes.decode(
        "utf-8",
        errors="replace",
    ).strip()


def extract_pdf_text_with_fallback(
    pdf_bytes: bytes,
) -> tuple[str, dict]:
    """
    Extract PDF text normally and use OCR when needed.
    """

    direct_text = extract_text_from_pdf_bytes(
        pdf_bytes
    )

    if len(
        direct_text.strip()
    ) >= MIN_DIRECT_PDF_TEXT_LENGTH:
        return (
            direct_text,
            {
                "method": "direct_pdf_text",
                "ocr_used": False,
                "warnings": [],
            },
        )

    try:
        ocr_result = (
            extract_text_from_pdf_with_ocr(
                pdf_bytes=pdf_bytes,
                languages="eng+deu",
            )
        )

        return (
            ocr_result["text"],
            {
                "method": "ocr",
                "ocr_used": True,
                "warnings": (
                    ocr_result.get(
                        "warnings",
                        [],
                    )
                ),
                "page_count": (
                    ocr_result.get(
                        "page_count",
                        0,
                    )
                ),
                "processed_pages": (
                    ocr_result.get(
                        "processed_pages",
                        0,
                    )
                ),
            },
        )

    except OCRError as error:
        if direct_text.strip():
            return (
                direct_text,
                {
                    "method": "direct_pdf_text",
                    "ocr_used": False,
                    "warnings": [
                        (
                            "OCR fallback failed: "
                            f"{error}"
                        )
                    ],
                },
            )

        raise ValueError(
            "No readable text could be extracted "
            "from the PDF, and OCR also failed: "
            f"{error}"
        ) from error


def extract_document_text(
    uploaded_file,
) -> str:
    """
    Extract text from PDF, DOCX or TXT uploads.

    Scanned PDFs automatically use OCR.
    """

    if uploaded_file is None:
        raise ValueError(
            "No file was provided."
        )

    filename = getattr(
        uploaded_file,
        "name",
        "",
    )

    file_extension = Path(
        filename
    ).suffix.lower()

    file_bytes = read_uploaded_file_bytes(
        uploaded_file
    )

    if file_extension == ".pdf":
        extracted_text, _ = (
            extract_pdf_text_with_fallback(
                file_bytes
            )
        )

        return extracted_text

    if file_extension == ".docx":
        return extract_text_from_docx_bytes(
            file_bytes
        )

    if file_extension == ".txt":
        return extract_text_from_txt_bytes(
            file_bytes
        )

    raise ValueError(
        "Unsupported file type. "
        "Upload a PDF, DOCX or TXT file."
    )