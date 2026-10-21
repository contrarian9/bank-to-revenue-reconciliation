# Bank-to-Revenue Reconciliation

An open-source screening tool for comparing positive bank transaction amounts with reported monthly revenue and flagging differences for human review.

## What it does

- Accepts bank transaction and reported-revenue CSV files.
- Aggregates positive bank entries by month.
- Compares monthly bank credits with reported revenue.
- Flags months where the absolute difference exceeds a configurable threshold.
- Exports a CSV reconciliation report.
- Includes synthetic sample data and unit tests.

## What it does not do

A bank credit is not necessarily revenue. Credits may include loans, transfers between accounts, refunds, GST, capital contributions, customer advances, or other non-revenue items. This tool does not classify credits or establish completeness, occurrence, cut-off, or accounting correctness. Every flag requires human investigation. Do not upload confidential client data to an environment you do not control.

## Run locally

Python 3.10+ recommended.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

**macOS/Linux:**

```bash
source .venv/bin/activate
```

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Launch the app:

```bash
python -m streamlit run app.py
```

## Run tests

```bash
python -m pip install -r requirements.txt
python -m pip install pytest
python -m pytest -q
```

## CSV formats

Bank transactions (`bank_transactions.csv`):

| date | description | amount |
|---|---|---:|
| 2026-01-05 | Customer receipt | 80000 |

Reported revenue (`reported_revenue.csv`):

| month | reported_revenue |
|---|---:|
| 2026-01-01 | 125000 |

Dates can be any parseable date. The month field is normalized to its calendar month. Use positive values for credits and negative values for debits; only positive values are included in the bank-credit comparison.

## Roadmap

- Configurable credit classification (customer receipts, transfers, loans, refunds, taxes).
- Separate GST/tax and inter-account transfer handling.
- Evidence-linked exception notes.
- Excel input and output.
- Additional tests and contributor documentation.

## Contributing

Issues and pull requests are welcome. Please include tests for changes to reconciliation logic. Do not submit real client bank statements, PANs, account numbers, or other confidential information.

## Disclaimer

This software is an analytical aid, not accounting, tax, legal, audit, or investment advice. It does not replace professional judgment or verification against source documents.
