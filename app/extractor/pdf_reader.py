"""
pdf_reader.py — Extract text and tables from digital (text-layer) PDFs.

Why pdfplumber over PyMuPDF?
- pdfplumber is built specifically for table extraction. It uses pdfminer
  under the hood and gives you precise control over bounding boxes, which
  matters when bank statement columns shift across pages.
- PyMuPDF (fitz) is faster and better for rendering pages as images, but
  its table extraction is weaker for complex layouts.
- Rule of thumb: pdfplumber for structured data extraction, PyMuPDF for
  image/rendering tasks (which we use in ocr_reader.py).

Why does pdfplumber only work on digital PDFs?
- A digital PDF has a text layer: the actual characters are encoded in the
  file as vector data. pdfplumber reads that layer directly.
- A scanned PDF is just a photo of a page saved as PDF. There is no text
  layer — only pixels. pdfplumber finds nothing because there's nothing to
  find. That's why we need OCR as a fallback.
"""

import pdfplumber
from pathlib import Path
from typing import Optional


def is_digital_pdf(pdf_path: str) -> bool:
    """
    Check if a PDF has a text layer (digital) or is image-only (scanned).

    How it works:
    - Open the first page and try to extract text.
    - If we get back a meaningful string (>20 chars), it's digital.
    - If we get nothing or just whitespace, it's scanned.
    - We check only the first page for speed — if page 1 has text,
      the whole document almost certainly does too.
    """
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        # None means pdfplumber found no text objects at all
        # len check filters out PDFs with only a few stray characters
        return text is not None and len(text.strip()) > 20


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """
    Extract raw text from every page of a digital PDF.

    Returns a list of dicts, one per page:
    [
        {"page_number": 1, "text": "...raw text from page 1..."},
        {"page_number": 2, "text": "...raw text from page 2..."},
        ...
    ]

    Why return page-by-page instead of one big string?
    - Bank statements often span 3-6 pages. Keeping pages separate lets us
      track which page a transaction came from — useful for debugging parsing
      errors later ("the amount parsing broke on page 3").
    - You can always join them: "\n".join(p["text"] for p in pages)
    """
    pages = []

    # pdfplumber.open() is a context manager — it opens the PDF and
    # automatically closes the file handle when we exit the `with` block.
    # This prevents memory leaks from unclosed file handles.
    with pdfplumber.open(pdf_path) as pdf:

        # pdf.pages is a list of Page objects, one per page.
        # enumerate() gives us both the index (i) and the Page object.
        for i, page in enumerate(pdf.pages):

            # extract_text() reads all text objects on the page and joins
            # them into a single string, preserving rough spatial order
            # (top-to-bottom, left-to-right).
            # Returns None if the page has no text layer.
            text = page.extract_text()

            pages.append({
                "page_number": i + 1,  # 1-indexed for human readability
                "text": text or "",    # replace None with empty string
            })

    return pages


def extract_tables_from_pdf(pdf_path: str) -> list[dict]:
    """
    Extract tables from every page of a digital PDF.

    Why extract tables separately from text?
    - Bank statement transactions are in a table: date | description | debit | credit | balance
    - extract_text() flattens this into a string, which makes parsing columns
      much harder (you lose the column boundary information).
    - extract_tables() returns the actual 2D grid structure, which is far
      easier to turn into a DataFrame.

    Returns a list of dicts, one per page:
    [
        {
            "page_number": 1,
            "tables": [
                [["Date", "Description", "Debit", "Credit", "Balance"],
                 ["01 Jan 2024", "UPI-SWIGGY", "450.00", "", "84550.00"],
                 ...]
            ]
        },
        ...
    ]

    Each table is a list of rows. Each row is a list of cell strings.
    None means the cell was empty (e.g., a credit row has no debit value).
    """
    pages_with_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):

            # extract_tables() detects table boundaries by looking for
            # lines (ruling lines) that form a grid. Returns a list because
            # a single page can have multiple tables.
            tables = page.extract_tables()

            pages_with_tables.append({
                "page_number": i + 1,
                "tables": tables or [],  # replace None with empty list
            })

    return pages_with_tables


def extract_full(pdf_path: str) -> dict:
    """
    Main entry point: extract both text and tables from a digital PDF.

    This is the function the rest of the pipeline calls.
    Returns a single dict with everything from the document.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if not is_digital_pdf(pdf_path):
        raise ValueError(
            f"{path.name} appears to be a scanned PDF. "
            "Use ocr_reader.py for image-based PDFs."
        )

    return {
        "source": path.name,
        "pdf_type": "digital",
        "pages": extract_text_from_pdf(pdf_path),
        "tables": extract_tables_from_pdf(pdf_path),
    }
