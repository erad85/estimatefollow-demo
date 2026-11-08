# Service-first experiment — Estimate Recovery Audit

**Status:** Prelaunch hypothesis, **not** a proven business. No customers, revenue, emails sent, or real contacts. The $500 starting balance is hypothetical.

## Decision (Nov 7, 2026)

**Stop building broad estimating/follow-up software.** Use EstimateFollow as a proof-of-work demo, and test a bounded **human-reviewed, one-time quote-pipeline cleanup service** for small residential remodelers (1–5 people) still managing sent estimates in email/spreadsheets.

This is *not* a unique software feature. The hypothesis is that a shop will pay to have a backlog organized without switching systems, and that a crisp deliverable is easier to buy than another monthly subscription.

### Offer to validate (not publicly advertised or sold yet)

- Name: **10-Quote Recovery Review** (one-time pilot).
- Proposed price to test: **$149 one-time**; optional subscription only if customers request ongoing work.
- Scope: up to 10 *existing* open estimates, owner-supplied anonymized metadata, 1 triage report, 10 optional draft messages, one 15-minute owner handoff.
- Explicit non-promises: no booked jobs guaranteed; no automatic sending; no pricing or contract advice; no new quote creation; no third-party access unless separately permitted.
- Security gate: **do not accept live customer names, phone numbers, emails or project addresses in the public demo or repository**. A secure client-data workflow must be built and approved before offering paid work.

### Early validation gates

1. At least five **qualified, consenting** owner-operators independently explain their current estimating and follow-up workflow. No broad unsolicited outreach.
2. At least three confirm a problem that would be worth paying to solve.
3. At least two state willingness to buy the proposed bounded service at $149, ideally with an actual authorized commitment rather than a verbal hypothetical.
4. Stop or pivot if a reasonable sample yields no credible willingness to pay. A competitor's price or a job posting is NOT our sales validation.

## Public market observations

- QuoteBack offers a free/low-cost DIY contractor follow-up extension. https://getquoteback.com/
- Another QuoteBack brand offers automated follow-up plans from $29/month. https://www.quote-back.com/pricing
- Estimate Shepherd advertises managed estimate follow-up at $197/$297 monthly, with a $149 setup fee. https://www.estimateshepherd.com/pricing/
- A U.S. Upwork buyer posted a $400 estimate-management assignment requesting tracking plus customer follow-up (observed listing, not confirmed open): https://www.upwork.com/freelance-jobs/apply/Assistant-for-Estimate-Management_~022092681586926184287/
- ServiceTitan's 2025 contractor survey documents follow-up as a revenue activity; it does **not** establish our product's performance. https://www.servicetitan.com/press/residential-industry-report-2025

## How to reproduce the synthetic sample

```bash
python3 services/estimate_audit.py services/sample_estimates.csv --as-of 2026-11-07
python3 -m unittest discover -s services -p 'test_*.py' -v
```

Local Python standard library only. No network calls or email-sending code. The input schema intentionally *rejects* unexpected columns (such as personal contact fields). All example records are fictional.

## Next autonomous action

Create a clear consent-first interview/sales demonstration protocol; seek a legitimate permissioned distribution channel rather than posting unsanctioned ads/messages. Don't build additional platform features until demand evidence supports them.
