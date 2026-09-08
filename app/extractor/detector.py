"""
detector.py — Detect which extraction strategy to use for a given PDF.

This is the router that decides: pdfplumber (digital) or pytesseract (scanned)?
The rest of the pipeline doesn't need to know which path was taken —
it just gets back the same structured output either way.
"""

import pdfplumber


def detect_pdf_type(pdf_path: str) -> str:
    """
    Returns 'digital' or 'scanned' based on whether the PDF has a text layer.

    Strategy:
    - Sample the first 3 pages (or fewer if the doc is short).
    - Count how many characters are found across those pages.
    - If total characters > threshold, classify as digital.
    - Why 3 pages? Some PDFs have a cover image on page 1 but text on page 2.
      Sampling avoids false 'scanned' classification from cover pages.
    """
    CHAR_THRESHOLD = 100  # minimum chars across sampled pages to call it digital
    total_chars = 0

    with pdfplumber.open(pdf_path) as pdf:
        sample_pages = pdf.pages[:3]  # first 3 pages max
        for page in sample_pages:
            text = page.extract_text()
            if text:
                total_chars += len(text.strip())

    return "digital" if total_chars >= CHAR_THRESHOLD else "scanned"
