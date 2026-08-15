"""Document parser service for extracting text from PDF files in memory."""
import io
import logging
from typing import Tuple
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.utils.text_cleaner import clean_text, is_meaningful_text

logger = logging.getLogger(__name__)


class DocumentParsingError(Exception):
    """Custom exception raised when PDF document parsing fails."""
    def __init__(self, message: str, detail: str = ""):
        super().__init__(message)
        self.message = message
        self.detail = detail


def parse_pdf_bytes(pdf_bytes: bytes, filename: str = "document.pdf") -> Tuple[str, int]:
    """
    Parse a PDF from raw bytes in memory, extracting text from all pages.
    
    Returns:
        Tuple[str, int]: (Cleaned extracted text, Page count)
        
    Raises:
        DocumentParsingError: If file is empty, corrupted, encrypted, or lacks selectable text.
    """
    if not pdf_bytes or len(pdf_bytes) == 0:
        raise DocumentParsingError(
            message=f"The uploaded file '{filename}' is empty.",
            detail="Please upload a valid PDF document containing text."
        )

    # Check for basic PDF magic bytes
    if not pdf_bytes.startswith(b"%PDF"):
        raise DocumentParsingError(
            message=f"The file '{filename}' is not a valid PDF document.",
            detail="The file header does not match the PDF standard."
        )

    try:
        stream = io.BytesIO(pdf_bytes)
        reader = PdfReader(stream)

        if reader.is_encrypted:
            try:
                # Attempt empty password decryption
                reader.decrypt("")
            except Exception:
                raise DocumentParsingError(
                    message=f"The PDF '{filename}' is password-protected or encrypted.",
                    detail="Please remove the password from the PDF before uploading."
                )

        page_count = len(reader.pages)
        if page_count == 0:
            raise DocumentParsingError(
                message=f"The PDF '{filename}' contains no pages.",
                detail="Please upload a PDF document with at least one page."
            )

        extracted_pages = []
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    extracted_pages.append(page_text)
            except Exception as page_err:
                logger.warning(f"Failed to extract page {i+1} in '{filename}': {page_err}")
                continue

        combined_text = "\n\n".join(extracted_pages)
        cleaned = clean_text(combined_text)

        if not is_meaningful_text(cleaned, min_chars=30):
            raise DocumentParsingError(
                message=f"No selectable text found in '{filename}'.",
                detail=(
                    "This PDF may be a scanned image or photo. JobLens AI requires "
                    "a PDF with selectable text (such as one exported from Google Docs, "
                    "Word, or Canva)."
                )
            )

        return cleaned, page_count

    except PdfReadError as e:
        logger.error(f"PyPDF read error for '{filename}': {e}")
        raise DocumentParsingError(
            message=f"Could not read the PDF '{filename}'. The file may be damaged or corrupted.",
            detail=str(e)
        )
    except DocumentParsingError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error parsing PDF '{filename}': {e}")
        raise DocumentParsingError(
            message=f"An unexpected error occurred while reading '{filename}'.",
            detail=str(e)
        )
