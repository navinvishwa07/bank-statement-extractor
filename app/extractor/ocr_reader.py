"""
ocr_reader.py — Extract text from scanned (image-based) PDFs using OCR.

Why pytesseract?
- Tesseract is the most battle-tested open source OCR engine (originally
  developed at HP, maintained by Google since 2006).
- pytesseract is just the Python wrapper around it.
- For Indian bank statements, Tesseract's English model works well because
  bank PDFs use standard printed fonts — not handwriting.

Why pdf2image + pytesseract instead of just pytesseract directly on the PDF?
- pytesseract operates on images (PIL/numpy arrays), not PDFs.
- pdf2image uses poppler under the hood to convert each PDF page into a
  high-resolution image (default 200 DPI), then we OCR each image.
- Higher DPI = better OCR accuracy but slower. 200 DPI is the sweet spot
  for printed bank statements.

System requirement: Tesseract must be installed separately.
  macOS: brew install tesseract
  Ubuntu: apt install tesseract-ocr
"""

from pdf2image import convert_from_path
import pytesseract
from pathlib import Path


def extract_text_from_scanned_pdf(pdf_path: str, dpi: int = 200) -> list[dict]:
    """
    Convert each PDF page to an image, then run OCR on each image.

    Args:
        pdf_path: Path to the scanned PDF file.
        dpi: Resolution for page rendering. Higher = more accurate but slower.
             200 DPI is standard; use 300 for poor quality scans.

    Returns:
        Same format as pdf_reader.extract_text_from_pdf() — list of dicts
        with page_number and text. This consistent output shape means the
        parser layer doesn't need to know which extractor was used.
    """
    pages = []

    # convert_from_path() renders each PDF page as a PIL Image object.
    # It returns a list of images, one per page.
    images = convert_from_path(pdf_path, dpi=dpi)

    for i, image in enumerate(images):
        # image_to_string() runs Tesseract OCR on the PIL image.
        # lang="eng" uses the English language model.
        # config="--psm 6" tells Tesseract to treat the image as a
        # single uniform block of text (good for structured documents).
        # PSM = Page Segmentation Mode. Mode 6 works well for bank statements.
        text = pytesseract.image_to_string(image, lang="eng", config="--psm 6")

        pages.append({
            "page_number": i + 1,
            "text": text.strip(),
        })

    return pages
