"""Tạo các biểu đồ từ dữ liệu giao dịch."""
from pathlib import Path
import matplotlib.pyplot as plt
from storage import load_transactions
from analysis import spending_by_category, monthly_spending

CHART_DIR = Path(__file__).resolve().parent / "charts"
CHART_DIR.mkdir(exist_ok=True)


def create_charts():
    """Tạo pie chart, bar chart và line chart; trả về danh sách đường dẫn."""
    df = load_transactions()
    if df.empty or df[df["type"] == "expense"].empty:
        return []

    by_category = spending_by_category(df)
    monthly = monthly_spending(df)
    paths = []

    # 1. Pie chart: cơ cấu chi tiêu theo danh mục.
    plt.figure(figsize=(8, 6))
    plt.pie(
        by_category["total"],
        labels=by_category["category"],
        autopct="%1.1f%%",
        startangle=90,
    )
    plt.title("Cơ cấu chi tiêu theo danh mục")
    plt.tight_layout()
    path = CHART_DIR / "01_co_cau_chi_tieu.png"
    plt.savefig(path, dpi=160)
    plt.close()
    paths.append(path)

    # 2. Bar chart: so sánh tổng chi giữa các danh mục.
    plt.figure(figsize=(9, 6))
    plt.barh(by_category["category"][::-1], by_category["total"][::-1])
    plt.title("Chi tiêu theo danh mục")
    plt.xlabel("Số tiền (VNĐ)")
    plt.ylabel("Danh mục")
    plt.tight_layout()
    path = CHART_DIR / "02_chi_tieu_theo_danh_muc.png"
    plt.savefig(path, dpi=160)
    plt.close()
    paths.append(path)

    # 3. Line chart: xu hướng tổng chi theo tháng.
    plt.figure(figsize=(9, 6))
    plt.plot(monthly["month"], monthly["total"], marker="o")
    plt.title("Xu hướng chi tiêu theo tháng")
    plt.xlabel("Tháng")
    plt.ylabel("Số tiền (VNĐ)")
    plt.grid(True)
    plt.tight_layout()
    path = CHART_DIR / "03_xu_huong_chi_tieu.png"
    plt.savefig(path, dpi=160)
    plt.close()
    paths.append(path)

    return paths
