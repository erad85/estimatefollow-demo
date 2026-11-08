#!/usr/bin/env python3
"""Local-only quote pipeline audit. No network, no sending, no personal data columns.

Use ONLY with permission and sanitized data. All amounts are quoted opportunities,
NOT booked or recovered revenue.
"""
import argparse
import csv
import datetime as dt
from decimal import Decimal, InvalidOperation
from pathlib import Path

COLUMNS = ("estimate_id", "job_type", "amount_usd", "quote_sent", "last_contact",
           "status", "reply_received", "do_not_contact")
TERMINAL = {"won", "lost", "declined"}
VALID_STATUSES = TERMINAL | {"open", "sent", "pending"}
TRUE = {"true", "1", "yes", "y"}
FALSE = {"false", "0", "no", "n", ""}
MAX_ROWS = 5000

def parse_bool(value, field, rownum):
    val = (value or "").strip().lower()
    if val not in TRUE | FALSE:
        raise ValueError(f"Row {rownum}: invalid {field}")
    return val in TRUE

def parse_date(value, field, rownum):
    try:
        return dt.date.fromisoformat(value.strip())
    except (ValueError, AttributeError):
        raise ValueError(f"Row {rownum}: invalid {field} date (YYYY-MM-DD)")

def parse_money(value, rownum):
    try:
        amount = Decimal(value.replace(",", "").strip())
        if not amount.is_finite() or amount < 0 or amount > Decimal("100000000"):
            raise ValueError()
        return amount.quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError, AttributeError):
        raise ValueError(f"Row {rownum}: invalid or negative amount_usd")

def audit(path, as_of):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or set(reader.fieldnames) != set(COLUMNS):
            raise ValueError("Only sanitized columns are allowed: " + ", ".join(COLUMNS))
        results = []
        seen = set()
        for rownum, row in enumerate(reader, start=2):
            if None in row or any(v is None for v in row.values()):
                raise ValueError(f"Row {rownum}: malformed CSV column count")
            if rownum - 1 > MAX_ROWS:
                raise ValueError("Too many rows")
            ident = (row["estimate_id"] or "").strip()
            job = (row["job_type"] or "").strip()
            if not ident or not job or len(ident) > 50 or len(job) > 100 or any(c in ident + job for c in "\n\r|") or ident.lstrip().startswith(("=", "+", "-", "@")) or job.lstrip().startswith(("=", "+", "-", "@")):
                raise ValueError(f"Row {rownum}: invalid id or job type")
            if ident in seen:
                raise ValueError(f"Row {rownum}: duplicate estimate_id")
            seen.add(ident)
            amount = parse_money(row["amount_usd"], rownum)
            status = (row["status"] or "").strip().lower()
            if status not in VALID_STATUSES:
                raise ValueError(f"Row {rownum}: unknown status")
            replied = parse_bool(row["reply_received"], "reply_received", rownum)
            dnc = parse_bool(row["do_not_contact"], "do_not_contact", rownum)
            sent = parse_date(row["quote_sent"], "quote_sent", rownum)
            contact = parse_date(row["last_contact"], "last_contact", rownum) if (row["last_contact"] or "").strip() else sent
            if dnc or status in TERMINAL:
                category = "suppress"
                age = max(0, (as_of - contact).days)
            elif sent > as_of or contact > as_of or contact < sent:
                category = "review_date"
                age = 0
            else:
                age = (as_of - contact).days
                if dnc or status in TERMINAL:
                    category = "suppress"
                elif replied:
                    category = "owner_review_reply"
                elif (as_of - sent).days > 30:
                    category = "owner_review_old"
                elif age >= 7:
                    category = "follow_up_due"
                else:
                    category = "wait"
            results.append(dict(id=ident, job=job, amount=amount, sent=sent,
                                days_since_contact=age, action=category))
    return sorted(results, key=lambda x: (x["action"] != "follow_up_due", -x["days_since_contact"], -x["amount"], x["id"]))

def money(amount):
    return f"${amount:,.2f}"

def markdown(rows, as_of):
    due = [r for r in rows if r["action"] == "follow_up_due"]
    open_actions = {"follow_up_due", "wait", "owner_review_old", "owner_review_reply", "review_date"}
    open_total = sum((r["amount"] for r in rows if r["action"] in open_actions), Decimal("0"))
    due_total = sum((r["amount"] for r in due), Decimal("0"))
    lines = [
        "# Estimate pipeline review — synthetic/sample data",
        "",
        f"Review date: {as_of.isoformat()}",
        "",
        f"- Estimates reviewed: **{len(rows)}**",
        f"- Follow-up candidates: **{len(due)}** (quoted value {money(due_total)})",
        f"- Total open quoted opportunity: **{money(open_total)}**",
        "- **Quoted amounts are not revenue. No conversion or recovery is claimed.**",
        "",
        "## Triage",
        "",
        "| ID | Job type | Quote amount | Days since contact | Action |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for r in rows:
        action = r["action"].replace("_", " ")
        lines.append(f'| {r["id"]} | {r["job"]} | {money(r["amount"])} | {r["days_since_contact"]} | {action} |')
    lines += [
        "",
        "## Recommended operating procedure",
        "",
        "1. Owner confirms each eligible estimate is still valid and not already answered, rejected, booked, or opted out.",
        "2. Draft a short, relevant follow-up. Owner reviews and sends it manually through an appropriate existing channel.",
        "3. Never message suppressed, replied, or ambiguous-date records without owner review.",
        "4. Record the outcome and follow-up date in the owner's existing system.",
        "",
        "No messages were generated or sent. This audit processes sanitized information locally only.",
    ]
    return "\n".join(lines) + "\n"

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csv_file", type=Path)
    ap.add_argument("--as-of", type=dt.date.fromisoformat, default=dt.date.today())
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    report = markdown(audit(args.csv_file, args.as_of), args.as_of)
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")

if __name__ == "__main__":
    main()
