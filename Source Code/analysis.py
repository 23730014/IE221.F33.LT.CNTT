"""Tổng hợp số liệu và phân tích thói quen chi tiêu."""
import pandas as pd
from storage import load_transactions


def financial_summary(df=None):
    """Tính tổng thu, tổng chi, số dư và số giao dịch."""
    df = load_transactions() if df is None else df
    income = df.loc[df["type"] == "income", "amount"].sum() if not df.empty else 0
    expense = df.loc[df["type"] == "expense", "amount"].sum() if not df.empty else 0
    return {
        "income": float(income),
        "expense": float(expense),
        "balance": float(income - expense),
        "transactions": int(len(df)),
    }


def spending_by_category(df=None):
    """Tổng hợp chi tiêu theo danh mục, số giao dịch và tỷ trọng."""
    df = load_transactions() if df is None else df
    expense_df = df[df["type"] == "expense"].copy()

    if expense_df.empty:
        return pd.DataFrame(columns=["category", "total", "count", "percent"])

    result = (
        expense_df.groupby("category")["amount"]
        .agg(total="sum", count="count")
        .reset_index()
    )
    result["percent"] = result["total"] / result["total"].sum() * 100
    return result.sort_values("total", ascending=False).reset_index(drop=True)


def monthly_spending(df=None):
    """Tổng hợp chi tiêu theo tháng để tạo xu hướng."""
    df = load_transactions() if df is None else df
    expense_df = df[df["type"] == "expense"].copy()

    if expense_df.empty:
        return pd.DataFrame(columns=["month", "total"])

    expense_df["month"] = expense_df["date"].astype(str).str[:7]
    return (
        expense_df.groupby("month")["amount"]
        .sum()
        .reset_index(name="total")
        .sort_values("month")
    )


def spending_analysis(df=None):
    """Trả về các chỉ số chính phục vụ phần phân tích thói quen."""
    by_category = spending_by_category(df)
    total = float(by_category["total"].sum()) if not by_category.empty else 0.0
    count = int(by_category["count"].sum()) if not by_category.empty else 0

    return {
        "total_expense": total,
        "average_expense": total / count if count else 0.0,
        "top_category": str(by_category.iloc[0]["category"]) if not by_category.empty else None,
        "by_category": by_category,
        "monthly": monthly_spending(df),
    }
