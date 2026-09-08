# FinExtract AI 🏦

> Intelligent document processing pipeline for Indian bank statement PDFs — PDF in, structured financial data out.

## The Problem It Solves

Indian fintech analysts manually spend 20–40 minutes per loan application reading bank statements, calculating average income, identifying EMIs, and flagging irregular credits. FinExtract automates that entire extraction — no manual intervention.

## Pipeline (v1)

```
PDF Upload
    ↓
pdfplumber (digital PDFs) / OCR (scanned PDFs)
    ↓
Text Cleaning & Parsing
    ↓
Transaction Extraction (dates, amounts, descriptions)
    ↓
Categorization & Aggregation
    ↓
Groq LLM Summary (income, EMIs, cash flow insights)
    ↓
Structured JSON + Streamlit UI
```

## Tech Stack & Why

| Component | Library | Why |
|-----------|---------|-----|
| PDF Extraction | `pdfplumber` | Best table/text extraction for digital PDFs; preserves layout |
| OCR fallback | `pytesseract` | For scanned/image-based PDFs where no text layer exists |
| API layer | `FastAPI` | Async, automatic OpenAPI docs, faster than Flask |
| LLM Summary | `Groq (Llama 3)` | Fast inference, free tier, good at structured extraction |
| UI | `Streamlit` | Rapid prototyping for data apps, no frontend needed |

## Project Structure

```
bank-statement-extractor/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point
│   ├── extractor/
│   │   ├── __init__.py
│   │   ├── pdf_reader.py    # pdfplumber text/table extraction
│   │   ├── ocr_reader.py    # pytesseract fallback
│   │   └── detector.py      # detect if PDF is digital or scanned
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── transaction.py   # extract transactions from raw text
│   │   ├── cleaner.py       # clean UPI strings, normalize amounts
│   │   └── categorizer.py   # categorize transactions
│   ├── analyzer/
│   │   ├── __init__.py
│   │   └── summary.py       # income, EMI detection, cash flow
│   └── llm/
│       ├── __init__.py
│       └── groq_client.py   # Groq API for final narrative summary
├── streamlit_app/
│   └── app.py               # Streamlit UI
├── samples/                 # Sample PDFs for testing (gitignored if sensitive)
├── tests/
│   └── test_pdf_reader.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Getting Started

```bash
# 1. Clone and set up virtual environment
git clone https://github.com/navinvishwa07/bank-statement-extractor.git
cd bank-statement-extractor
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
cp .env.example .env
# Add your GROQ_API_KEY in .env

# 4. Run the API
uvicorn app.main:app --reload

# 5. Run the Streamlit UI
streamlit run streamlit_app/app.py
```

## What It Outputs

```json
{
  "bank": "HDFC",
  "account_holder": "Navin Vishwa",
  "statement_period": "2024-01 to 2024-06",
  "transactions": [...],
  "summary": {
    "avg_monthly_income": 85000,
    "avg_monthly_expense": 52000,
    "recurring_emis": [
      { "merchant": "HDFC Home Loan", "amount": 18500, "frequency": "monthly" }
    ],
    "irregular_credits": [...],
    "cash_flow_trend": "stable"
  },
  "narrative": "The account shows stable income around ₹85,000/month..."
}
```

## Build Status

- [x] Project scaffold
- [ ] PDF text extraction (pdfplumber)
- [ ] OCR fallback (pytesseract)
- [ ] Transaction parser
- [ ] Amount/date normalizer (Indian formats: ₹1,23,456 / Cr/Dr)
- [ ] Categorizer
- [ ] Groq summary
- [ ] FastAPI endpoints
- [ ] Streamlit UI
- [ ] Deployed (Render / Railway)