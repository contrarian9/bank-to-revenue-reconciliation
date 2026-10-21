# Bank-to-Revenue Reconciliation

An open-source review aid for comparing bank credits with reported revenue. Classify transactions before reconciliation to separate revenue from transfers, loans, refunds, and other non-revenue credits.

This tool supports screening and investigation. It is not an audit opinion or proof of revenue.

## What it does

- Accepts bank transaction and reported-revenue CSV files.
- Lets users classify bank transactions before reconciliation.
- Includes only credits classified as revenue in the revenue comparison.
- Reports excluded non-revenue credits and unclassified credits separately.
- Compares monthly revenue-classified credits with reported revenue.
- Flags monthly differences exceeding a configurable threshold.
- Exports the reconciliation report and classified transactions as CSV.
- Includes synthetic sample data and automated tests.

## What it does not do

A bank credit is not necessarily revenue. Classification requires human judgment and supporting evidence. The tool does not independently establish completeness, occurrence, cut-off, or accounting correctness. Review all flagged differences and unclassified credits.

Do not upload confidential client data to an environment you do not control.

## Run locally

Python 3.10 or later is recommended.

Create and activate a virtual environment:

**macOS/Linux**

    python3 -m venv .venv
    source .venv/bin/activate

**Windows PowerShell**

    python -m venv .venv
    .venv\Scripts\Activate.ps1

Install dependencies and launch the app:

    python -m pip install -r requirements.txt
    python -m streamlit run app.py

## Run tests

Install the dependencies and run:

    python -m pip install -r requirements.txt
    python -m pip install pytest
    python -m pytest -q

## CSV formats

**Bank transactions**

Required columns: `date`, `description`, `amount`.

**Reported revenue**

Required columns: `month`, `reported_revenue`.

The app includes downloadable synthetic sample CSVs. Dates must be parseable, and the month field is normalized to its calendar month. Positive bank amounts represent credits. Classify each credit carefully; do not assume all credits are revenue.

## Contributing

Issues and pull requests are welcome. Please include tests for changes to reconciliation logic. Never submit real client bank statements, account numbers, PANs, or other confidential information.

## Disclaimer

This software is an analytical aid, not accounting, tax, legal, audit, or investment advice. It does not replace professional judgment or verification against source documents.
