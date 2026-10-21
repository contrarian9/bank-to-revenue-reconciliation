
import pandas as pd
import pytest

from reconcile import reconcile


def test_reconcile_flags_difference_over_tolerance():
    bank = pd.DataFrame({
        "date": ["2026-01-05", "2026-01-20"],
        "description": ["Customer receipt", "Transfer"],
        "amount": [80000, 30000],
    })
    revenue = pd.DataFrame({
        "month": ["2026-01-01"],
        "reported_revenue": [100000],
    })

    result = reconcile(bank, revenue, tolerance=5000)

    assert result.loc[0, "bank_credits"] == 110000
    assert result.loc[0, "difference_bank_minus_revenue"] == 10000
    assert bool(result.loc[0, "review_flag"]) is True


def test_reconcile_handles_month_present_in_only_one_file():
    bank = pd.DataFrame({
        "date": ["2026-01-05"],
        "description": ["Receipt"],
        "amount": [500],
    })
    revenue = pd.DataFrame({
        "month": ["2026-02-01"],
        "reported_revenue": [400],
    })

    result = reconcile(bank, revenue, tolerance=0)

    assert set(result["month"]) == {"2026-01", "2026-02"}


def test_rejects_invalid_date():
    bank = pd.DataFrame({
        "date": ["bad"],
        "description": ["Receipt"],
        "amount": [500],
    })
    revenue = pd.DataFrame({
        "month": ["2026-02-01"],
        "reported_revenue": [400],
    })

    with pytest.raises(ValueError):
        reconcile(bank, revenue)


def test_classification_excludes_non_revenue_credits():
    bank = pd.DataFrame({
        "date": ["2026-01-05", "2026-01-10", "2026-01-15"],
        "description": ["Customer receipt", "Loan", "Bank transfer"],
        "amount": [80000, 50000, 20000],
        "category": ["revenue", "loan", "transfer"],
    })
    revenue = pd.DataFrame({
        "month": ["2026-01-01"],
        "reported_revenue": [80000],
    })

    result = reconcile(bank, revenue, tolerance=0)
    row = result.iloc[0]

    assert row["bank_credits"] == 80000
    assert row["excluded_credits"] == 70000
    assert row["unclassified_credits"] == 0
    assert bool(row["review_flag"]) is False


def test_classification_keeps_unclassified_credits_visible():
    bank = pd.DataFrame({
        "date": ["2026-01-05", "2026-01-10"],
        "description": ["Customer receipt", "Unknown credit"],
        "amount": [80000, 25000],
        "category": ["revenue", ""],
    })
    revenue = pd.DataFrame({
        "month": ["2026-01-01"],
        "reported_revenue": [80000],
    })

    result = reconcile(bank, revenue, tolerance=0)
    row = result.iloc[0]

    assert row["bank_credits"] == 80000
    assert row["unclassified_credits"] == 25000
    assert bool(row["review_flag"]) is False


def test_classification_is_case_and_whitespace_tolerant():
    bank = pd.DataFrame({
        "date": ["2026-01-05", "2026-01-10"],
        "description": ["Receipt", "Loan"],
        "amount": [80000, 50000],
        "category": [" Revenue ", " LOAN "],
    })
    revenue = pd.DataFrame({
        "month": ["2026-01-01"],
        "reported_revenue": [80000],
    })

    result = reconcile(bank, revenue, tolerance=0)
    row = result.iloc[0]

    assert row["bank_credits"] == 80000
    assert row["excluded_credits"] == 50000
