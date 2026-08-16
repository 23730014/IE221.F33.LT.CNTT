"""Thiết lập ngân sách và cảnh báo theo mức sử dụng."""
import pandas as pd
from storage import load_budgets, save_budgets, load_transactions
from transaction import CATEGORIES, validate_month


def set_budget(month, category, limit):
    """Tạo mới hoặc cập nhật hạn mức ngân sách."""
    validate_month(month)
    if category not in CATEGORIES:
        raise ValueError("Danh mục không hợp lệ.")
    limit = float(limit)
    if limit <= 0:
        raise ValueError("Ngân sách phải lớn hơn 0.")

    df = load_budgets()
    mask = (df["month"].astype(str) == month) & (df["category"] == category)

    if mask.any():
        df.loc[mask, "limit"] = limit
    else:
        new_row = pd.DataFrame([{"month": month, "category": category, "limit": limit}])
        df = pd.concat([df, new_row], ignore_index=True)

    save_budgets(df)


def budget_report(month):
    """So sánh chi tiêu tháng với ngân sách từng danh mục."""
    validate_month(month)
    budgets = load_budgets()
    transactions = load_transactions()
    budgets = budgets[budgets["month"].astype(str) == month].copy()

    if budgets.empty:
        return pd.DataFrame(columns=["category", "limit", "spent", "percent", "status"])

    if transactions.empty:
        spent = pd.Series(dtype=float)
    else:
        expense = transactions[
            (transactions["type"] == "expense")
            & transactions["date"].astype(str).str.startswith(month)
        ]
        spent = expense.groupby("category")["amount"].sum()

    rows = []
    for _, row in budgets.iterrows():
        category = row["category"]
        limit = float(row["limit"])
        actual = float(spent.get(category, 0))
        percent = actual / limit * 100

        if percent < 80:
            status = "Bình thường"
        elif percent < 100:
            status = "Cảnh báo"
        else:
            status = "Vượt ngân sách"

        rows.append({
            "category": category,
            "limit": limit,
            "spent": actual,
            "percent": percent,
            "status": status,
        })

    return pd.DataFrame(rows)
