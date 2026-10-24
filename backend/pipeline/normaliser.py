import re
from dateutil import parser as dateparser


# ── Amount / Date / Description helpers ───────────────────


def normalise_amount(amount_str: str) -> float:
    """Converts any Indian amount format to a plain float.
    Handles: ₹1,23,456.00 / 1,23,456 Cr / INR 123456
    """
    amount_str = str(amount_str)
    amount_str = amount_str.replace("₹", "").replace("INR", "").replace(",", "").strip()
    amount_str = re.sub(r"[CcDd][Rr]?$", "", amount_str).strip()
    try:
        return float(amount_str)
    except ValueError:
        return 0.0


def normalise_date(date_str: str) -> str:
    """Converts any date format to YYYY-MM-DD.
    Handles: 01/08/2024 / 01-Aug-24 / Aug 01 2024
    """
    try:
        return dateparser.parse(date_str, dayfirst=True).strftime("%Y-%m-%d")
    except Exception:
        return None


def normalise_description(description: str) -> str:
    """Cleans UPI strings and noisy transaction descriptions.
    UPI/CR/4293847238/Swiggy India Pvt/YESB → Swiggy India Pvt
    """
    description = description.strip()
    if description.upper().startswith("UPI/"):
        parts = description.split("/")
        if len(parts) >= 4:
            return parts[3].strip()
    return description


# ── Bank detection ─────────────────────────────────────────


def detect_bank(raw_text: str) -> str:
    """Detects which bank the statement is from based on header text."""
    text_upper = raw_text.upper().replace(" ", "")
    if "HDFCBANK" in text_upper:
        return "HDFC"
    if "STATEBANKOFINDIAS" in text_upper or "SBIBANK" in text_upper:
        return "SBI"
    if "AXISBANK" in text_upper:
        return "AXIS"
    if "ICICIBANK" in text_upper:
        return "ICICI"
    return "UNKNOWN"

# ── HDFC parser ────────────────────────────────────────────


def parse_hdfc_transactions(raw_text: str) -> list[dict]:
    """
    Parses raw pdfplumber text from an HDFC statement.
    HDFC format: Date | Narration | Chq/Ref No | Value Dt | Withdrawal | Deposit | Closing Balance
    """
    lines = raw_text.split("\n")

    # Find where the transaction table starts
    start_index = None
    for i, line in enumerate(lines):
        if "Date" in line and "Narration" in line:
            start_index = i + 1
            break

    if start_index is None:
        return []

    # Find where the table ends
    end_index = len(lines)
    for i, line in enumerate(lines):
        if "STATEMENT SUMMARY" in line or "StatementSummary" in line.replace(" ", ""):
            end_index = i
            break

    transaction_lines = lines[start_index:end_index]

    # Extract transaction rows
    date_pattern = re.compile(r"^\d{2}/\d{2}/\d{2}")
    transactions = []
    current = None

    for line in transaction_lines:
        line = line.strip()
        if not line:
            continue

        if date_pattern.match(line):
            if current:
                transactions.append(current)

            parts = line.split()
            date_str = parts[0]

            try:
                closing_balance = normalise_amount(parts[-1])
                amount = normalise_amount(parts[-2])

                # Find the value date (second DD/MM/YY in the line)
                # Ref number sits just before it
                date_tokens = [
                    i for i, p in enumerate(parts)
                    if re.match(r"\d{2}/\d{2}/\d{2}", p)
                ]

                if len(date_tokens) >= 2:
                    value_date_idx = date_tokens[1]
                    ref_idx = value_date_idx - 1
                    description_parts = parts[1:ref_idx]
                else:
                    description_parts = parts[1:-3]

                description = " ".join(description_parts)

            except (IndexError, ValueError):
                continue

            current = {
                "date": normalise_date(date_str),
                "description": normalise_description(description),
                "amount": amount,
                "closing_balance": closing_balance,
                "type": "debit",
                "raw": line,
            }

        else:
            # Continuation line — append to current description
            if current:
                current["description"] += " " + line.strip()

    if current:
        transactions.append(current)

    # Determine credit vs debit using closing balance movement
    for i in range(1, len(transactions)):
        prev_balance = transactions[i - 1]["closing_balance"]
        curr_balance = transactions[i]["closing_balance"]
        if curr_balance > prev_balance:
            transactions[i]["type"] = "credit"
        else:
            transactions[i]["type"] = "debit"

    # Clean up internal fields
    for t in transactions:
        t.pop("closing_balance", None)
        t.pop("raw", None)

    return [t for t in transactions if t["date"] and t["amount"] > 0]


# ── SBI parser (stub — add when you have an SBI sample) ───


def parse_sbi_transactions(raw_text: str) -> list[dict]:
    """SBI format is different — implement when sample is available."""
    raise NotImplementedError("SBI parser not yet implemented")


# ── Router — the only function the pipeline calls ─────────


def parse_transactions(raw_text: str) -> list[dict]:
    """
    Detects the bank and routes to the correct parser.
    This is the single entry point for the rest of the pipeline.
    Always returns the same transaction dict shape regardless of bank.
    """
    bank = detect_bank(raw_text)

    if bank == "HDFC":
        return parse_hdfc_transactions(raw_text)
    elif bank == "SBI":
        return parse_sbi_transactions(raw_text)
    else:
        raise ValueError(f"Unsupported bank: {bank}. Supported: HDFC, SBI") 