import sys
import os

# Add parent directory to path so we can import from backend
sys.path.insert(0, os.path.dirname(__file__))

from backend.db.supabase import insert_document, get_document, update_document_status

# Insert a test document
doc = insert_document(filename="test_hdfc.pdf", bank="HDFC")
print("Inserted:", doc)

# Fetch it back
fetched = get_document(doc["id"])
print("Fetched:", fetched)

# Update status
update_document_status(doc["id"], status="processing")
print("Status updated")
