import datetime as dt
import tempfile
import unittest
from pathlib import Path
from estimate_audit import audit, markdown

ROOT = Path(__file__).parent

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.rows = audit(ROOT / "sample_estimates.csv", dt.date(2026, 11, 7))

    def test_triage(self):
        actual = {r["id"]: r["action"] for r in self.rows}
        self.assertEqual(actual, {
            "EF-001": "follow_up_due",
            "EF-002": "wait",
            "EF-003": "follow_up_due",
            "EF-004": "suppress",
            "EF-005": "owner_review_reply",
            "EF-006": "owner_review_old",
            "EF-007": "suppress",
            "EF-008": "wait",
        })

    def test_open_not_revenue(self):
        report = markdown(self.rows, dt.date(2026,11,7))
        self.assertIn("not revenue", report.lower())
        self.assertIn("Follow-up candidates: **2**", report)
        self.assertIn("No messages were generated or sent", report)

    def test_reject_sensitive_extra_columns(self):
        original = (ROOT / "sample_estimates.csv").read_text()
        with tempfile.TemporaryDirectory() as path:
            p = Path(path) / "bad.csv"
            p.write_text(original.replace("estimate_id,job_type", "estimate_id,customer_email,job_type"), encoding="utf-8")
            with self.assertRaises(ValueError):
                audit(p, dt.date(2026, 11, 7))

    def test_reject_invalid_amount(self):
        original = (ROOT / "sample_estimates.csv").read_text()
        with tempfile.TemporaryDirectory() as path:
            p = Path(path) / "bad.csv"
            p.write_text(original.replace("14500", "-100"), encoding="utf-8")
            with self.assertRaises(ValueError):
                audit(p, dt.date(2026, 11, 7))

if __name__ == "__main__":
    unittest.main()
