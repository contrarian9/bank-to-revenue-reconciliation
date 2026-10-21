
from __future__ import annotations

import pandas as pd
import streamlit as st

from reconcile import reconcile, NON_REVENUE_CATEGORIES

st.set_page_config(
    page_title="Bank-to-Revenue Reconciliation",
    page_icon="📊",
    layout="wide",
)

st.title("Bank-to-Revenue Reconciliation")
st.caption(
    "An open-source review aid for comparing bank credits with reported "
    "revenue. Not an audit opinion or proof of revenue."
)

st.markdown("""
Upload two CSV files:

- **Bank transactions:** `date`, `description`, `amount`
- **Reported revenue:** `month`, `reported_revenue`

Positive amounts are treated as credits. Classifying a credit as revenue
requires human judgment. Do not upload confidential client data to an
environment you do not control.
""")

with st.expander("Download sample CSV files"):
    bank_sample = pd.DataFrame({
        "date": ["2026-01-05", "2026-01-10", "2026-01-15"],
        "description": [
            "Customer receipt",
            "Inter-account transfer",
            "Unidentified credit",
        ],
        "amount": [80000, 20000, 5000],
        "category": ["revenue", "transfer", ""],
    })
    revenue_sample = pd.DataFrame({
        "month": ["2026-01-01"],
        "reported_revenue": [80000],
    })
    st.download_button(
        "Sample bank transactions",
        bank_sample.to_csv(index=False).encode("utf-8"),
        "bank_transactions_sample.csv",
        "text/csv",
    )
    st.download_button(
        "Sample reported revenue",
        revenue_sample.to_csv(index=False).encode("utf-8"),
        "reported_revenue_sample.csv",
        "text/csv",
    )

bank_file = st.file_uploader(
    "Bank transactions CSV", type=["csv"], key="bank"
)
revenue_file = st.file_uploader(
    "Reported revenue CSV", type=["csv"], key="revenue"
)
tolerance = st.number_input(
    "Flag if absolute difference exceeds (₹)",
    min_value=0.0,
    value=10000.0,
    step=1000.0,
)

CATEGORY_OPTIONS = [
    "unclassified",
    "revenue",
    *sorted(NON_REVENUE_CATEGORIES),
]

if bank_file and revenue_file:
    try:
        bank = pd.read_csv(bank_file)
        revenue = pd.read_csv(revenue_file)

        required_bank = {"date", "description", "amount"}
        required_revenue = {"month", "reported_revenue"}

        if not required_bank.issubset(bank.columns):
            st.error("Bank CSV must contain: date, description, amount.")
            st.stop()

        if not required_revenue.issubset(revenue.columns):
            st.error("Revenue CSV must contain: month, reported_revenue.")
            st.stop()

        bank["date"] = pd.to_datetime(bank["date"], errors="coerce")
        bank["amount"] = pd.to_numeric(bank["amount"], errors="coerce")
        revenue["month"] = pd.to_datetime(
            revenue["month"], errors="coerce"
        )
        revenue["reported_revenue"] = pd.to_numeric(
            revenue["reported_revenue"], errors="coerce"
        )

        if bank["date"].isna().any() or bank["amount"].isna().any():
            st.error("Some bank dates or amounts are invalid. Correct them and upload again.")
            st.stop()

        if (
            revenue["month"].isna().any()
            or revenue["reported_revenue"].isna().any()
        ):
            st.error("Some revenue months or values are invalid. Correct them and upload again.")
            st.stop()

        if "category" not in bank.columns:
            bank["category"] = "unclassified"
        else:
            bank["category"] = (
                bank["category"]
                .fillna("unclassified")
                .astype(str)
                .str.strip()
                .str.lower()
                .str.replace(" ", "_")
            )
            bank.loc[bank["category"].eq(""), "category"] = "unclassified"

        st.subheader("Classify bank transactions")
        st.write(
            "Choose a category for each transaction. Unknown credits remain "
            "unclassified and are excluded from the revenue comparison."
        )

        edited_bank = st.data_editor(
            bank,
            use_container_width=True,
            hide_index=True,
            disabled=["date", "description", "amount"],
            column_config={
                "category": st.column_config.SelectboxColumn(
                    "Category",
                    options=CATEGORY_OPTIONS,
                    required=True,
                )
            },
            key="transaction_editor",
        )

        result = reconcile(
            edited_bank,
            revenue,
            tolerance=float(tolerance),
        )

        st.subheader("Monthly comparison")
        c1, c2, c3 = st.columns(3)
        c1.metric(
            "Credits classified as revenue",
            f"₹{result['bank_credits'].sum():,.2f}",
        )
        c2.metric(
            "Reported revenue",
            f"₹{result['reported_revenue'].sum():,.2f}",
        )
        c3.metric(
            "Net difference",
            f"₹{result['difference_bank_minus_revenue'].sum():,.2f}",
        )

        st.dataframe(result, use_container_width=True, hide_index=True)

        if "excluded_credits" in result.columns:
            st.subheader("Credits excluded from revenue")
            st.metric(
                "Classified non-revenue credits",
                f"₹{result['excluded_credits'].sum():,.2f}",
            )
            st.metric(
                "Unclassified credits requiring review",
                f"₹{result['unclassified_credits'].sum():,.2f}",
            )

        flagged = result[result["review_flag"]]
        st.subheader("Months requiring review")

        if flagged.empty:
            st.success("No monthly difference exceeds the selected threshold.")
        else:
            st.warning(
                f"{len(flagged)} month(s) exceed the selected threshold. "
                "Investigate each difference; a flag is not evidence of an error."
            )
            st.dataframe(flagged, use_container_width=True, hide_index=True)

        st.subheader("Transaction detail")
        st.dataframe(
            edited_bank.sort_values("date"),
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download reconciliation report",
            result.to_csv(index=False).encode("utf-8"),
            "reconciliation_report.csv",
            "text/csv",
        )
        st.download_button(
            "Download classified transactions",
            edited_bank.to_csv(index=False).encode("utf-8"),
            "classified_bank_transactions.csv",
            "text/csv",
        )

    except Exception as exc:
        st.error(f"Could not process the files: {exc}")
else:
    st.info("Upload both CSV files to run the comparison.")
