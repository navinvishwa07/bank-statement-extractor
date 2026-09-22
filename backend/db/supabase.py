import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialise the Supabase client once — reused across the app
url: str = os.environ["SUPABASE_URL"]
key: str = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(url, key)


# ── Documents ──────────────────────────────────────────────

def insert_document(filename: str, bank: str) -> dict:
    """Create a document record when a PDF is uploaded."""
    response = (
        supabase.table("documents")
        .insert({"filename": filename, "bank": bank, "status": "pending"})
        .execute()
    )
    return response.data[0]


def update_document_status(document_id: str, status: str) -> None:
    """Update status as the pipeline progresses."""
    supabase.table("documents").update({"status": status}).eq("id", document_id).execute()


def get_document(document_id: str) -> dict:
    """Fetch a single document by ID."""
    response = supabase.table("documents").select("*").eq("id", document_id).execute()
    return response.data[0] if response.data else None


# ── Transactions ───────────────────────────────────────────

def insert_transactions(document_id: str, transactions: list[dict]) -> None:
    """Bulk insert all transactions for a document."""
    rows = [
        {
            "document_id": document_id,
            "date": t["date"],
            "description": t["description"],
            "amount": t["amount"],
            "type": t["type"],      # 'credit' or 'debit'
        }
        for t in transactions
    ]
    supabase.table("transactions").insert(rows).execute()


def get_transactions(document_id: str) -> list[dict]:
    """Fetch all transactions for a document."""
    response = (
        supabase.table("transactions")
        .select("*")
        .eq("document_id", document_id)
        .order("date")
        .execute()
    )
    return response.data


# ── Reports ────────────────────────────────────────────────

def insert_report(document_id: str, report: dict) -> dict:
    """Store the LLM-generated report."""
    response = (
        supabase.table("reports")
        .insert({
            "document_id": document_id,
            "avg_monthly_income": report["avg_monthly_income"],
            "emis": report["emis"],
            "irregular_credits": report["irregular_credits"],
            "cash_flow": report["cash_flow"],
            "summary": report["summary"],
        })
        .execute()
    )
    return response.data[0]


def get_report(document_id: str) -> dict:
    """Fetch the report for a document."""
    response = (
        supabase.table("reports")
        .select("*")
        .eq("document_id", document_id)
        .execute()
    )
    return response.data[0] if response.data else None
