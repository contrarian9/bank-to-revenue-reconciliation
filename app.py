from __future__ import annotations

import io
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Bank-to-Revenue Reconciliation", page_icon="📊", layout="wide")
st.title("Bank-to-Revenue Reconciliation")
st.caption("An open-source review aid for comparing bank credits with reported revenue. Not an audit opinion or proof of revenue.")

st.markdown("""
Upload two CSV files:
- **Bank transactions:** `date`, `description`, `amount`
- **Reported revenue:** `month`, `reported_revenue`

Use positive amounts for bank credits. This first version compares monthly bank credits with reported revenue; it does not automatically decide whether a credit is revenue.
""")

with st.expander("Download sample CSV files"):
    bank_sample = pd.read_csv("sample_data/bank_transactions.csv")
    revenue_sample = pd.read_csv("sample_data/reported_revenue.csv")
    st.download_button("Sample bank transactions", bank_sample.to_csv(index=False).encode(), "bank_transactions_sample.csv", "text/csv")
    st.download_button("Sample reported revenue", revenue_sample.to_csv(index=False).encode(), "reported_revenue_sample.csv", "text/csv")

bank_file = st.file_uploader("Bank transactions CSV", type=["csv"], key="bank")
revenue_file = st.file_uploader("Reported revenue CSV", type=["csv"], key="revenue")
tolerance = st.number_input("Flag if absolute difference exceeds (₹)", min_value=0.0, value=10000.0, step=1000.0)

def month_key(values):
    return pd.to_datetime(values, errors="coerce").dt.to_period("M").astype("string")

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
        revenue["month"] = pd.to_datetime(revenue["month"], errors="coerce")
        revenue["reported_revenue"] = pd.to_numeric(revenue["reported_revenue"], errors="coerce")

        if bank["date"].isna().any() or bank["amount"].isna().any():
            st.error("Some bank dates or amounts are invalid. Correct them and upload again.")
            st.stop()
        if revenue["month"].isna().any() or revenue["reported_revenue"].isna().any():
            st.error("Some revenue months or values are invalid. Correct them and upload again.")
            st.stop()

        bank["month"] = bank["date"].dt.to_period("M").astype("string")
        revenue["month"] = revenue["month"].dt.to_period("M").astype("string")

        # All positive bank entries are treated as credits in this initial version.
        # Users must review non-revenue credits (loans, transfers, refunds, etc.).
        bank_monthly = bank.groupby("month", as_index=False).agg(
            bank_credits=("amount", lambda s: s[s > 0].sum()),
            transaction_count=("amount", "size"),
        )
        revenue_monthly = revenue.groupby("month", as_index=False)["reported_revenue"].sum()
        result = bank_monthly.merge(revenue_monthly, on="month", how="outer").fillna(0)
        result["difference_bank_minus_revenue"] = result["bank_credits"] - result["reported_revenue"]
        result["absolute_difference"] = result["difference_bank_minus_revenue"].abs()
        result["review_flag"] = result["absolute_difference"] > tolerance
        result = result.sort_values("month")

        st.subheader("Monthly comparison")
        c1, c2, c3 = st.columns(3)
        c1.metric("Bank credits", f"₹{result['bank_credits'].sum():,.2f}")
        c2.metric("Reported revenue", f"₹{result['reported_revenue'].sum():,.2f}")
        c3.metric("Net difference", f"₹{result['difference_bank_minus_revenue'].sum():,.2f}")
        st.dataframe(result, use_container_width=True, hide_index=True)
        flagged = result[result["review_flag"]]
        st.subheader("Months requiring review")
        if flagged.empty:
            st.success("No monthly difference exceeds the selected threshold.")
        else:
            st.warning(f"{len(flagged)} month(s) exceed the selected threshold. Investigate each difference; a flag is not evidence of an error.")
            st.dataframe(flagged, use_container_width=True, hide_index=True)

        st.subheader("Transaction detail")
        st.dataframe(bank.sort_values("date"), use_container_width=True, hide_index=True)
        st.download_button(
            "Download reconciliation report",
            result.to_csv(index=False).encode("utf-8"),
            "reconciliation_report.csv",
            "text/csv",
        )
    except Exception as exc:
        st.error(f"Could not process the files: {exc}")
else:
    st.info("Upload both CSV files to run the comparison.")
