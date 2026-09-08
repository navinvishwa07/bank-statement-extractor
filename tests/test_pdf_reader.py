"""
test_pdf_reader.py — Tests for the PDF extraction module.

Run with: pytest tests/ -v
"""

import pytest
from pathlib import Path
from app.extractor.pdf_reader import (
    is_digital_pdf,
    extract_text_from_pdf,
    extract_tables_from_pdf,
    extract_full,
)
from app.extractor.detector import detect_pdf_type


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLES_DIR = Path(__file__).parent.parent / "samples"


def get_sample_pdf(name: str) -> str:
    """Return path to a sample PDF. Skip test if file doesn't exist."""
    path = SAMPLES_DIR / name
    if not path.exists():
        pytest.skip(f"Sample PDF not found: {path}. Add a PDF to samples/ to run this test.")
    return str(path)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_extract_text_returns_list():
    """extract_text_from_pdf should return a list."""
    pdf_path = get_sample_pdf("sample_hdfc.pdf")
    result = extract_text_from_pdf(pdf_path)
    assert isinstance(result, list), "Expected a list of pages"


def test_each_page_has_required_keys():
    """Each page dict must have 'page_number' and 'text' keys."""
    pdf_path = get_sample_pdf("sample_hdfc.pdf")
    pages = extract_text_from_pdf(pdf_path)
    for page in pages:
        assert "page_number" in page
        assert "text" in page


def test_page_numbers_are_sequential():
    """Page numbers should start at 1 and increment by 1."""
    pdf_path = get_sample_pdf("sample_hdfc.pdf")
    pages = extract_text_from_pdf(pdf_path)
    for i, page in enumerate(pages):
        assert page["page_number"] == i + 1


def test_digital_pdf_detected_correctly():
    """A real bank statement PDF should be classified as 'digital'."""
    pdf_path = get_sample_pdf("sample_hdfc.pdf")
    assert detect_pdf_type(pdf_path) == "digital"


def test_extract_full_raises_on_missing_file():
    """extract_full should raise FileNotFoundError for nonexistent files."""
    with pytest.raises(FileNotFoundError):
        extract_full("/nonexistent/path/file.pdf")


def test_extract_full_output_shape():
    """extract_full should return a dict with expected keys."""
    pdf_path = get_sample_pdf("sample_hdfc.pdf")
    result = extract_full(pdf_path)
    assert "source" in result
    assert "pdf_type" in result
    assert "pages" in result
    assert "tables" in result
    assert result["pdf_type"] == "digital"
