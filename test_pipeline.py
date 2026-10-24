import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from pipeline.detector import detect_pdf_type
from pipeline.extractor import extract_text
from pipeline.normaliser import normalise_amount, normalise_date, normalise_description, parse_transactions

# ── Normaliser unit tests ──
print("── Normaliser Tests ──")
print(normalise_amount("₹1,23,456.00"))
print(normalise_amount("1,23,456 Cr"))
print(normalise_amount("INR 85000"))
print(normalise_date("01/08/2024"))
print(normalise_date("01-Aug-24"))
print(normalise_description("UPI/CR/4293847238/Swiggy India Pvt/YESB"))
print(normalise_description("SALARY CREDIT AUGUST"))

# ── PDF pipeline test ──
PDF_PATH = "sample.pdf"

if os.path.exists(PDF_PATH):
    pdf_type = detect_pdf_type(PDF_PATH)
    print(f"\n── PDF Type: {pdf_type} ──")

    text = extract_text(PDF_PATH, pdf_type)

    print("\n── Parsing transactions ──")
    transactions = parse_transactions(text)
    print(f"Found {len(transactions)} transactions\n")

    for t in transactions[:10]:
        print(f"  {t['date']} | {t['type']:6} | ₹{t['amount']:>10.2f} | {t['description'][:50]}")
else:
    print("\nNo sample.pdf found")