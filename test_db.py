import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from db.supabase import (
    insert_document,
    get_document,
    update_document_status,
    insert_transactions,
    get_transactions,
    insert_report,
    get_report,
)

print("── Test 1: Insert document ──")
doc = insert_document(filename="test_hdfc.pdf", bank="HDFC")
print(f"Created: {doc}")
doc_id = doc["id"]

print("\n── Test 2: Fetch document ──")
fetched = get_document(doc_id)
print(f"Fetched: {fetched}")

print("\n── Test 3: Update status ──")
update_document_status(doc_id, "processing")
updated = get_document(doc_id)
print(f"Status is now: {updated['status']}")

print("\n── Test 4: Insert transactions ──")
test_transactions = [
    {"date": "2024-01-15", "description": "Swiggy India Pvt", "amount": 450.00, "type": "debit"},
    {"date": "2024-01-16", "description": "SALARY CREDIT", "amount": 85000.00, "type": "credit"},
    {"date": "2024-01-17", "description": "HDFC HOME LOAN EMI", "amount": 22000.00, "type": "debit"},
]
insert_transactions(doc_id, test_transactions)
print("Transactions inserted")

print("\n── Test 5: Fetch transactions ──")
txns = get_transactions(doc_id)
print(f"Fetched {len(txns)} transactions:")
for t in txns:
    print(f"  {t['date']} | {t['description']} | {t['amount']} | {t['type']}")

print("\n── Test 6: Insert report ──")
test_report = {
    "avg_monthly_income": 85000.00,
    "emis": [{"name": "HDFC Home Loan", "amount": 22000}],
    "irregular_credits": [],
    "cash_flow": {"january": {"income": 85000, "expenses": 22450}},
    "summary": "Stable salaried income with one EMI detected. No irregular credits.",
}
report = insert_report(doc_id, test_report)
print(f"Report inserted: {report}")

print("\n── Test 7: Fetch report ──")
fetched_report = get_report(doc_id)
print(f"Summary: {fetched_report['summary']}")

print("\n── All tests passed ──")