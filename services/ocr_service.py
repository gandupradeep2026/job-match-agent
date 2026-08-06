import io
import shutil
from pathlib import Path
from typing import Any

import fitz
import pytesseract
from PIL import Image


DEFAULT_OCR_LANGUAGES = "eng+deu"
DEFAULT_DPI = 220
MIN_PAGE_TEXT_LENGTH = 40


class OCRError(Exception):
    """
    Raised when OCR processing fails.
    """


def find_tesseract_executable() -> str:
    """
    Find the installed Tesseract executable.

    First checks PATH, then the common Windows location.
    """

    path_result = shutil.which(
        "tesseract"
    )

    if path_result:
        return path_result

    windows_path = Path(
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    if windows_path.exists():
        return str(
            windows_path
        )

    raise OCRError(
        "Tesseract could not be found. "
        "Install it or add it to Windows PATH."
    )


def configure_tesseract() -> str:
    """
    Configure pytesseract with the detected executable.
    """

    executable_path = (
        find_tesseract_executable()
    )

    pytesseract.pytesseract.tesseract_cmd = (
        executable_path
    )

    return executable_path


def get_available_languages() -> list[str]:
    """
    Return OCR languages available to Tesseract.
    """

    configure_tesseract()

    try:
        languages = (
            pytesseract.get_languages(
                config=""
            )
        )

    except Exception as error:
        raise OCRError(
            "Tesseract languages could not be read."
        ) from error

    return sorted(
        languages
    )


def validate_ocr_languages(
    requested_languages: str,
) -> str:
    """
    Validate requested OCR language codes.

    Example:
        eng+deu
    """

    available_languages = set(
        get_available_languages()
    )

    requested_codes = [
        code.strip()
        for code in requested_languages.split(
            "+"
        )
        if code.strip()
    ]

    missing_languages = [
        code
        for code in requested_codes
        if code not in available_languages
    ]

    if missing_languages:
        raise OCRError(
            "The following OCR language data is missing: "
            + ", ".join(
                missing_languages
            )
        )

    return "+".join(
        requested_codes
    )


def pixmap_to_image(
    pixmap: fitz.Pixmap,
) -> Image.Image:
    """
    Convert a PyMuPDF pixmap into a Pillow image.
    """

    image_bytes = pixmap.tobytes(
        "png"
    )

    return Image.open(
        io.BytesIO(
            image_bytes
        )
    ).convert(
        "RGB"
    )


def ocr_image(
    image: Image.Image,
    languages: str = DEFAULT_OCR_LANGUAGES,
) -> str:
    """
    Extract text from one image using Tesseract.
    """

    configure_tesseract()

    validated_languages = (
        validate_ocr_languages(
            languages
        )
    )

    try:
        text = pytesseract.image_to_string(
            image,
            lang=validated_languages,
            config="--oem 3 --psm 6",
        )

    except Exception as error:
        raise OCRError(
            "OCR failed while processing an image."
        ) from error

    return text.strip()


def render_pdf_page(
    page: fitz.Page,
    dpi: int = DEFAULT_DPI,
) -> Image.Image:
    """
    Render one PDF page as a high-resolution image.
    """

    zoom = dpi / 72

    matrix = fitz.Matrix(
        zoom,
        zoom,
    )

    pixmap = page.get_pixmap(
        matrix=matrix,
        alpha=False,
    )

    return pixmap_to_image(
        pixmap
    )


def extract_text_from_pdf_with_ocr(
    pdf_bytes: bytes,
    languages: str = DEFAULT_OCR_LANGUAGES,
    dpi: int = DEFAULT_DPI,
    max_pages: int = 30,
) -> dict[str, Any]:
    """
    OCR a complete PDF and return text plus diagnostics.
    """

    if not pdf_bytes:
        raise OCRError(
            "The PDF file is empty."
        )

    configure_tesseract()

    validated_languages = (
        validate_ocr_languages(
            languages
        )
    )

    try:
        document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf",
        )

    except Exception as error:
        raise OCRError(
            "The uploaded file is not a readable PDF."
        ) from error

    try:
        page_count = document.page_count

        if page_count <= 0:
            raise OCRError(
                "The PDF contains no pages."
            )

        pages_to_process = min(
            page_count,
            max_pages,
        )

        extracted_pages = []
        failed_pages = []

        for page_index in range(
            pages_to_process
        ):
            try:
                page = document.load_page(
                    page_index
                )

                image = render_pdf_page(
                    page,
                    dpi=dpi,
                )

                page_text = ocr_image(
                    image,
                    languages=validated_languages,
                )

                extracted_pages.append(
                    page_text
                )

            except Exception as error:
                failed_pages.append(
                    {
                        "page": page_index + 1,
                        "error": str(error),
                    }
                )

                extracted_pages.append(
                    ""
                )

        combined_text = "\n\n".join(
            page_text
            for page_text in extracted_pages
            if page_text.strip()
        ).strip()

        if not combined_text:
            raise OCRError(
                "OCR completed but no readable text was found."
            )

        warnings = []

        if page_count > max_pages:
            warnings.append(
                f"Only the first {max_pages} pages were processed."
            )

        if failed_pages:
            warnings.append(
                f"{len(failed_pages)} page(s) could not be processed."
            )

        return {
            "text": combined_text,
            "page_count": page_count,
            "processed_pages": pages_to_process,
            "failed_pages": failed_pages,
            "languages": validated_languages,
            "dpi": dpi,
            "warnings": warnings,
        }

    finally:
        document.close()