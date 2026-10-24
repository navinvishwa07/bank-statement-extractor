import pdfplumber
import easyocr
from pdf2image import convert_from_path

def extract_digital(filepath: str) -> str:
    """Extract text from a digital PDF using pdfplumber."""
    full_text = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
    return "\n".join(full_text)


def extract_scanned(filepath: str) -> str:
    """Extract text from a scanned PDF using EasyOCR."""
    reader = easyocr.Reader(["en"])
    images = convert_from_path(filepath)
    full_text = []
    for image in images:
        results = reader.readtext(image, detail=0)
        full_text.append("\n".join(results))
    return "\n".join(full_text)


def extract_text(filepath: str, pdf_type: str) -> str:
    """Route to the correct extractor based on PDF type."""
    if pdf_type == "digital":
        return extract_digital(filepath)
    return extract_scanned(filepath)