"""Core reconciliation logic for the Bank-to-Revenue Reconciliation Tool."""
from __future__ import annotations
import pandas as pd

BANK_COLUMNS = {"date", "description", "amount"}
REVENUE_COLUMNS = {"month", "reported_revenue"}

def reconcile(bank: pd.DataFrame, revenue: pd.DataFrame, tolerance: float = 10_000.0) -> pd.DataFrame:
    """Compare monthly positive bank credits with reported revenue.

    This is a screening calculation only. Positive bank credits may include loans,
    transfers, refunds, capital contributions, or other non-revenue items.
    """
    missing_bank = BANK_COLUMNS - set(bank.columns)
    missing_revenue = REVENUE_COLUMNS - set(revenue.columns)
    if missing_bank:
        raise ValueError(f"Bank data missing columns: {', '.join(sorted(missing_bank))}")
    if missing_revenue:
        raise ValueError(f"Revenue data missing columns: {', '.join(sorted(missing_revenue))}")

    b = bank.copy()
    r = revenue.copy()
    b["date"] = pd.to_datetime(b["date"], errors="coerce")
    b["amount"] = pd.to_numeric(b["amount"], errors="coerce")
    r["month"] = pd.to_datetime(r["month"], errors="coerce")
    r["reported_revenue"] = pd.to_numeric(r["reported_revenue"], errors="coerce")

    if b["date"].isna().any() or b["amount"].isna().any():
        raise ValueError("Bank data contains invalid dates or amounts.")
    if r["month"].isna().any() or r["reported_revenue"].isna().any():
        raise ValueError("Revenue data contains invalid months or values.")
    if tolerance < 0:
        raise ValueError("Tolerance must be zero or greater.")

    b["month"] = b["date"].dt.to_period("M").astype(str)
    r["month"] = r["month"].dt.to_period("M").astype(str)
    bm = b.groupby("month", as_index=False).agg(
        bank_credits=("amount", lambda s: s[s > 0].sum()),
        transaction_count=("amount", "size"),
    )
    rm = r.groupby("month", as_index=False)["reported_revenue"].sum()
    out = bm.merge(rm, on="month", how="outer").fillna(0)
    out["difference_bank_minus_revenue"] = out["bank_credits"] - out["reported_revenue"]
    out["absolute_difference"] = out["difference_bank_minus_revenue"].abs()
    out["review_flag"] = out["absolute_difference"] > tolerance
    return out.sort_values("month").reset_index(drop=True)
