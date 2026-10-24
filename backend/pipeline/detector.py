import pdfplumber

def detect_pdf_type(filepath: str) -> str:
    """
    Returns 'digital' if the PDF has a text layer.
    Returns 'scanned' if it's an image-based PDF.
    """
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():
                return "digital"
    return "scanned"