import pandas as pd
import pytest
from reconcile import reconcile

def test_reconcile_flags_difference_over_tolerance():
    bank = pd.DataFrame({
        "date": ["2026-01-05", "2026-01-20"],
        "description": ["Customer receipt", "Transfer"],
        "amount": [80000, 30000],
    })
    revenue = pd.DataFrame({"month": ["2026-01-01"], "reported_revenue": [100000]})
    result = reconcile(bank, revenue, tolerance=5000)
    assert result.loc[0, "bank_credits"] == 110000
    assert result.loc[0, "difference_bank_minus_revenue"] == 10000
    assert bool(result.loc[0, "review_flag"]) is True

def test_reconcile_handles_month_present_in_only_one_file():
    bank = pd.DataFrame({"date": ["2026-01-05"], "description": ["Receipt"], "amount": [500]})
    revenue = pd.DataFrame({"month": ["2026-02-01"], "reported_revenue": [400]})
    result = reconcile(bank, revenue, tolerance=0)
    assert set(result["month"]) == {"2026-01", "2026-02"}

def test_rejects_invalid_date():
    bank = pd.DataFrame({"date": ["bad"], "description": ["Receipt"], "amount": [500]})
    revenue = pd.DataFrame({"month": ["2026-02-01"], "reported_revenue": [400]})
    with pytest.raises(ValueError):
        reconcile(bank, revenue)
