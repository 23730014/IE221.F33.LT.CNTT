"""Kiểm thử tự động các chức năng cốt lõi.

Các test này chỉ đọc dữ liệu hiện có hoặc sử dụng DataFrame tạm thời,
không làm thay đổi dataset demo.
"""
import pandas as pd
from analysis import financial_summary, spending_by_category, monthly_spending
from budget import budget_report
from storage import load_transactions
from transaction import filter_transactions
from visualization import create_charts


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    df = load_transactions()
    check(len(df) == 120, "Dataset phải có 120 giao dịch.")
    check(df["date"].astype(str).str[:7].nunique() == 4, "Dataset phải có đúng 4 tháng.")

    summary = financial_summary(df)
    check(summary["income"] == 48_000_000, "Tổng thu không đúng.")
    check(summary["expense"] == 31_958_379, "Tổng chi không đúng.")
    check(summary["balance"] == 16_041_621, "Số dư không đúng.")

    filtered = filter_transactions(
        start_date="2026-06-01",
        end_date="2026-07-31",
        kind="expense",
        category="Ăn uống",
        min_amount=50_000,
        max_amount=150_000,
    )
    check(not filtered.empty, "Bộ lọc nâng cao phải trả về dữ liệu.")
    check((filtered["amount"] >= 50_000).all(), "Lỗi cận dưới lọc tiền.")
    check((filtered["amount"] <= 150_000).all(), "Lỗi cận trên lọc tiền.")
    check((filtered["category"] == "Ăn uống").all(), "Lỗi lọc danh mục.")

    by_category = spending_by_category(df)
    check(by_category.iloc[0]["category"] == "Hóa đơn", "Danh mục chi cao nhất phải là Hóa đơn.")

    monthly = monthly_spending(df)
    check(len(monthly) == 4, "Phải có 4 tháng trong thống kê.")

    budget = budget_report("2026-07")
    bill = budget.loc[budget["category"] == "Hóa đơn"].iloc[0]
    check(bill["status"] == "Vượt ngân sách", "Hóa đơn tháng 07 phải vượt ngân sách.")

    charts = create_charts()
    check(len(charts) == 3, "Phải tạo đúng 3 biểu đồ.")

    print("PASS - Dataset: 120 giao dịch / 4 tháng")
    print("PASS - Tổng thu: 48,000,000 đ")
    print("PASS - Tổng chi: 31,958,379 đ")
    print("PASS - Số dư: 16,041,621 đ")
    print("PASS - Lọc nâng cao")
    print("PASS - Phân tích theo danh mục/tháng")
    print("PASS - Cảnh báo vượt ngân sách")
    print("PASS - Sinh 3 biểu đồ")
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
