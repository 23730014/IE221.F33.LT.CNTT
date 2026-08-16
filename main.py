"""
HỆ THỐNG QUẢN LÝ CHI TIÊU CÁ NHÂN
=================================

Đề tài: Hệ thống quản lý chi tiêu cá nhân và phân tích thói quen tài chính

Mục tiêu:
- Quản lý các giao dịch thu/chi.
- Tìm kiếm và lọc giao dịch.
- Tính tổng thu, tổng chi và số dư.
- Quản lý ngân sách theo danh mục.
- Cảnh báo khi chi tiêu vượt ngân sách.
- Phân tích thói quen chi tiêu.
- Xuất báo cáo và biểu đồ.

Cách chạy:
    python main.py

Thư viện cần cài:
    pip install pandas matplotlib

Dữ liệu được lưu tại:
    data/transactions.csv
    data/budgets.csv
"""

import csv
import os
from datetime import datetime
from collections import defaultdict

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 1. CẤU HÌNH
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

TRANSACTION_FILE = os.path.join(DATA_DIR, "transactions.csv")
BUDGET_FILE = os.path.join(DATA_DIR, "budgets.csv")

TRANSACTION_FIELDS = [
    "id",
    "date",
    "type",
    "category",
    "amount",
    "description",
]

BUDGET_FIELDS = [
    "month",
    "category",
    "limit",
]


# Các danh mục được sử dụng trong chương trình.
CATEGORIES = [
    "Ăn uống",
    "Đi lại",
    "Mua sắm",
    "Học tập",
    "Giải trí",
    "Hóa đơn",
    "Y tế",
    "Khác",
]


# ============================================================
# 2. KHỞI TẠO FILE DỮ LIỆU
# ============================================================

def initialize_files():
    """
    Tạo thư mục và file dữ liệu nếu chưa tồn tại.

    Đây là bước cần thiết để chương trình có thể chạy ngay
    trên máy mới mà không cần tạo file CSV thủ công.
    """

    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(TRANSACTION_FILE):
        with open(
            TRANSACTION_FILE,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=TRANSACTION_FIELDS)
            writer.writeheader()

    if not os.path.exists(BUDGET_FILE):
        with open(
            BUDGET_FILE,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=BUDGET_FIELDS)
            writer.writeheader()


# ============================================================
# 3. HÀM HỖ TRỢ
# ============================================================

def format_money(value):
    """
    Chuyển số tiền sang dạng dễ đọc.

    Ví dụ:
        1500000 -> 1,500,000 đ
    """
    return f"{float(value):,.0f} đ"


def input_positive_number(message):
    """
    Yêu cầu người dùng nhập một số dương.

    Hàm lặp lại cho đến khi người dùng nhập đúng.
    """

    while True:
        try:
            value = float(input(message).replace(",", "").strip())

            if value <= 0:
                print("❌ Số tiền phải lớn hơn 0.")
                continue

            return value

        except ValueError:
            print("❌ Vui lòng nhập một số hợp lệ.")


def input_date(message="Ngày giao dịch (YYYY-MM-DD): "):
    """
    Nhập ngày và kiểm tra định dạng YYYY-MM-DD.
    """

    while True:
        value = input(message).strip()

        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value

        except ValueError:
            print("❌ Ngày không hợp lệ. Ví dụ: 2026-08-16")


def choose_type():
    """
    Cho người dùng lựa chọn loại giao dịch:
    1 = Thu nhập
    2 = Chi tiêu
    """

    while True:
        print("\n1. Thu nhập")
        print("2. Chi tiêu")

        choice = input("Chọn loại giao dịch: ").strip()

        if choice == "1":
            return "income"

        if choice == "2":
            return "expense"

        print("❌ Lựa chọn không hợp lệ.")


def choose_category():
    """
    Hiển thị danh sách danh mục và trả về danh mục được chọn.
    """

    print("\n--- DANH MỤC ---")

    for i, category in enumerate(CATEGORIES, start=1):
        print(f"{i}. {category}")

    while True:
        try:
            choice = int(input("Chọn danh mục: "))

            if 1 <= choice <= len(CATEGORIES):
                return CATEGORIES[choice - 1]

        except ValueError:
            pass

        print("❌ Vui lòng chọn đúng số danh mục.")


def get_next_transaction_id(df):
    """
    Tạo ID giao dịch mới.

    Nếu chưa có giao dịch -> ID = 1.
    Nếu đã có -> lấy ID lớn nhất + 1.
    """

    if df.empty:
        return 1

    return int(df["id"].astype(int).max()) + 1


# ============================================================
# 4. ĐỌC / GHI DỮ LIỆU
# ============================================================

def load_transactions():
    """
    Đọc danh sách giao dịch từ CSV.

    Trả về:
        pandas.DataFrame
    """

    try:
        df = pd.read_csv(TRANSACTION_FILE, encoding="utf-8-sig")

        if df.empty:
            return pd.DataFrame(columns=TRANSACTION_FIELDS)

        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

        return df

    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=TRANSACTION_FIELDS)


def save_transactions(df):
    """
    Lưu DataFrame giao dịch vào file CSV.
    """

    df.to_csv(
        TRANSACTION_FILE,
        index=False,
        encoding="utf-8-sig"
    )


def load_budgets():
    """
    Đọc ngân sách từ file CSV.
    """

    try:
        df = pd.read_csv(BUDGET_FILE, encoding="utf-8-sig")

        if df.empty:
            return pd.DataFrame(columns=BUDGET_FIELDS)

        df["limit"] = pd.to_numeric(df["limit"], errors="coerce").fillna(0)

        return df

    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=BUDGET_FIELDS)


def save_budgets(df):
    """
    Lưu ngân sách vào CSV.
    """

    df.to_csv(
        BUDGET_FILE,
        index=False,
        encoding="utf-8-sig"
    )


# ============================================================
# 5. CRUD GIAO DỊCH
# ============================================================

def add_transaction():
    """
    Thêm một giao dịch mới.
    """

    df = load_transactions()

    print("\n========== THÊM GIAO DỊCH ==========")

    date = input_date()
    transaction_type = choose_type()
    category = choose_category()
    amount = input_positive_number("Số tiền: ")

    description = input("Mô tả: ").strip()

    new_transaction = {
        "id": get_next_transaction_id(df),
        "date": date,
        "type": transaction_type,
        "category": category,
        "amount": amount,
        "description": description,
    }

    df = pd.concat(
        [df, pd.DataFrame([new_transaction])],
        ignore_index=True
    )

    save_transactions(df)

    print("✅ Đã thêm giao dịch thành công.")


def show_transactions(df=None):
    """
    Hiển thị danh sách giao dịch.
    """

    if df is None:
        df = load_transactions()

    print("\n========== DANH SÁCH GIAO DỊCH ==========")

    if df.empty:
        print("Chưa có giao dịch.")
        return

    display_df = df.copy()

    display_df["Loại"] = display_df["type"].map({
        "income": "Thu",
        "expense": "Chi",
    })

    display_df["Số tiền"] = display_df["amount"].apply(format_money)

    display_df = display_df[
        ["id", "date", "Loại", "category", "Số tiền", "description"]
    ]

    display_df.columns = [
        "ID",
        "Ngày",
        "Loại",
        "Danh mục",
        "Số tiền",
        "Mô tả",
    ]

    print(display_df.to_string(index=False))


def edit_transaction():
    """
    Sửa thông tin một giao dịch đã tồn tại.
    """

    df = load_transactions()

    if df.empty:
        print("❌ Chưa có giao dịch.")
        return

    show_transactions(df)

    try:
        transaction_id = int(input("\nNhập ID cần sửa: "))
    except ValueError:
        print("❌ ID không hợp lệ.")
        return

    indexes = df.index[df["id"].astype(int) == transaction_id].tolist()

    if not indexes:
        print("❌ Không tìm thấy giao dịch.")
        return

    index = indexes[0]

    print("\nNhập thông tin mới:")

    df.loc[index, "date"] = input_date()
    df.loc[index, "type"] = choose_type()
    df.loc[index, "category"] = choose_category()
    df.loc[index, "amount"] = input_positive_number("Số tiền mới: ")
    df.loc[index, "description"] = input("Mô tả mới: ").strip()

    save_transactions(df)

    print("✅ Đã cập nhật giao dịch.")


def delete_transaction():
    """
    Xóa một giao dịch theo ID.
    """

    df = load_transactions()

    if df.empty:
        print("❌ Chưa có giao dịch.")
        return

    show_transactions(df)

    try:
        transaction_id = int(input("\nNhập ID cần xóa: "))
    except ValueError:
        print("❌ ID không hợp lệ.")
        return

    if transaction_id not in df["id"].astype(int).values:
        print("❌ Không tìm thấy giao dịch.")
        return

    confirm = input("Bạn chắc chắn muốn xóa? (y/n): ").lower()

    if confirm != "y":
        print("Đã hủy.")
        return

    df = df[df["id"].astype(int) != transaction_id]

    save_transactions(df)

    print("✅ Đã xóa giao dịch.")


# ============================================================
# 6. TÌM KIẾM / LỌC
# ============================================================

def search_transactions():
    """
    Tìm kiếm giao dịch theo từ khóa.

    Từ khóa có thể xuất hiện trong:
    - ngày
    - loại
    - danh mục
    - mô tả
    """

    df = load_transactions()

    if df.empty:
        print("❌ Chưa có giao dịch.")
        return

    keyword = input("\nNhập từ khóa cần tìm: ").strip().lower()

    mask = (
        df["date"].astype(str).str.lower().str.contains(keyword)
        | df["type"].astype(str).str.lower().str.contains(keyword)
        | df["category"].astype(str).str.lower().str.contains(keyword)
        | df["description"].astype(str).str.lower().str.contains(keyword)
    )

    result = df[mask]

    if result.empty:
        print("Không tìm thấy giao dịch phù hợp.")
    else:
        show_transactions(result)


def filter_by_month():
    """
    Lọc giao dịch theo tháng.

    Ví dụ nhập:
        2026-08
    """

    df = load_transactions()

    if df.empty:
        print("❌ Chưa có giao dịch.")
        return

    month = input("Nhập tháng cần lọc (YYYY-MM): ").strip()

    result = df[df["date"].astype(str).str.startswith(month)]

    if result.empty:
        print("Không có giao dịch trong tháng này.")
    else:
        show_transactions(result)


# ============================================================
# 7. TỔNG QUAN TÀI CHÍNH
# ============================================================

def financial_summary():
    """
    Tính:
    - Tổng thu nhập
    - Tổng chi tiêu
    - Số dư
    - Số giao dịch
    """

    df = load_transactions()

    print("\n========== TỔNG QUAN TÀI CHÍNH ==========")

    if df.empty:
        print("Chưa có dữ liệu.")
        return

    total_income = df.loc[
        df["type"] == "income", "amount"
    ].sum()

    total_expense = df.loc[
        df["type"] == "expense", "amount"
    ].sum()

    balance = total_income - total_expense

    print(f"Tổng thu nhập : {format_money(total_income)}")
    print(f"Tổng chi tiêu : {format_money(total_expense)}")
    print(f"Số dư         : {format_money(balance)}")
    print(f"Số giao dịch  : {len(df)}")


# ============================================================
# 8. NGÂN SÁCH
# ============================================================

def set_budget():
    """
    Thiết lập hoặc cập nhật ngân sách cho một danh mục trong một tháng.
    """

    df = load_budgets()

    print("\n========== THIẾT LẬP NGÂN SÁCH ==========")

    while True:
        month = input("Tháng (YYYY-MM): ").strip()

        try:
            datetime.strptime(month + "-01", "%Y-%m-%d")
            break
        except ValueError:
            print("❌ Tháng không hợp lệ.")

    category = choose_category()
    limit = input_positive_number("Hạn mức ngân sách: ")

    mask = (
        (df["month"].astype(str) == month)
        & (df["category"].astype(str) == category)
    )

    if mask.any():
        df.loc[mask, "limit"] = limit
    else:
        new_budget = pd.DataFrame([{
            "month": month,
            "category": category,
            "limit": limit,
        }])

        df = pd.concat([df, new_budget], ignore_index=True)

    save_budgets(df)

    print("✅ Đã lưu ngân sách.")


def budget_report():
    """
    So sánh chi tiêu thực tế với ngân sách.

    Quy ước:
        < 80%     : Bình thường
        80%-<100% : Cảnh báo
        >= 100%   : Vượt ngân sách
    """

    budget_df = load_budgets()
    transaction_df = load_transactions()

    print("\n========== BÁO CÁO NGÂN SÁCH ==========")

    if budget_df.empty:
        print("Chưa thiết lập ngân sách.")
        return

    month = input("Nhập tháng cần xem (YYYY-MM): ").strip()

    budget_df = budget_df[
        budget_df["month"].astype(str) == month
    ]

    if budget_df.empty:
        print("Không có ngân sách cho tháng này.")
        return

    if not transaction_df.empty:
        transaction_df["date"] = transaction_df["date"].astype(str)

        monthly_expense = transaction_df[
            (transaction_df["date"].str.startswith(month))
            & (transaction_df["type"] == "expense")
        ]

        spent = monthly_expense.groupby("category")["amount"].sum()
    else:
        spent = pd.Series(dtype=float)

    for _, row in budget_df.iterrows():

        category = row["category"]
        limit = float(row["limit"])

        actual = float(spent.get(category, 0))

        percent = actual / limit * 100

        if percent < 80:
            status = "Bình thường"
        elif percent < 100:
            status = "Cảnh báo"
        else:
            status = "VƯỢT NGÂN SÁCH"

        print(
            f"\n{category}"
            f"\n  Ngân sách : {format_money(limit)}"
            f"\n  Đã chi    : {format_money(actual)}"
            f"\n  Sử dụng   : {percent:.1f}%"
            f"\n  Trạng thái: {status}"
        )


# ============================================================
# 9. PHÂN TÍCH THÓI QUEN CHI TIÊU
# ============================================================

def spending_analysis():
    """
    Phân tích dữ liệu chi tiêu.

    Kết quả:
    - Tổng chi.
    - Chi trung bình.
    - Danh mục chi nhiều nhất.
    - Tỷ trọng từng danh mục.
    - Số lượng giao dịch.
    """

    df = load_transactions()

    print("\n========== PHÂN TÍCH THÓI QUEN CHI TIÊU ==========")

    if df.empty:
        print("Chưa có dữ liệu.")
        return

    expense_df = df[df["type"] == "expense"].copy()

    if expense_df.empty:
        print("Chưa có khoản chi nào.")
        return

    total_expense = expense_df["amount"].sum()
    average_expense = expense_df["amount"].mean()

    category_summary = (
        expense_df
        .groupby("category")["amount"]
        .agg(["sum", "count"])
        .sort_values("sum", ascending=False)
    )

    category_summary["percent"] = (
        category_summary["sum"] / total_expense * 100
    )

    top_category = category_summary.index[0]

    print(f"Tổng chi tiêu          : {format_money(total_expense)}")
    print(f"Chi trung bình/giao dịch: {format_money(average_expense)}")
    print(f"Danh mục chi nhiều nhất : {top_category}")

    print("\n--- CHI TIÊU THEO DANH MỤC ---")

    for category, row in category_summary.iterrows():
        print(
            f"{category:12}"
            f" | {format_money(row['sum']):>15}"
            f" | {row['percent']:6.1f}%"
            f" | {int(row['count'])} giao dịch"
        )

    print(
        "\n💡 Gợi ý: Hãy ưu tiên xem xét các danh mục có tỷ trọng "
        "cao nhất để điều chỉnh ngân sách."
    )


# ============================================================
# 10. BIỂU ĐỒ
# ============================================================

def create_charts():
    """
    Tạo 3 biểu đồ:
    1. Cơ cấu chi tiêu theo danh mục.
    2. So sánh chi tiêu theo danh mục.
    3. Xu hướng tổng chi theo tháng.
    """

    df = load_transactions()

    if df.empty:
        print("❌ Chưa có dữ liệu.")
        return

    expense_df = df[df["type"] == "expense"].copy()

    if expense_df.empty:
        print("❌ Chưa có khoản chi.")
        return

    # --------------------------------------------------------
    # Biểu đồ 1: Biểu đồ tròn
    # --------------------------------------------------------

    category_total = expense_df.groupby("category")["amount"].sum()

    plt.figure(figsize=(8, 6))

    plt.pie(
        category_total.values,
        labels=category_total.index,
        autopct="%1.1f%%",
        startangle=90,
    )

    plt.title("Cơ cấu chi tiêu theo danh mục")
    plt.tight_layout()

    chart1 = os.path.join(DATA_DIR, "01_co_cau_chi_tieu.png")
    plt.savefig(chart1, dpi=150)
    plt.show()

    # --------------------------------------------------------
    # Biểu đồ 2: Biểu đồ cột
    # --------------------------------------------------------

    plt.figure(figsize=(10, 6))

    category_total.sort_values().plot(kind="barh")

    plt.title("Chi tiêu theo danh mục")
    plt.xlabel("Số tiền (VNĐ)")
    plt.ylabel("Danh mục")
    plt.tight_layout()

    chart2 = os.path.join(DATA_DIR, "02_chi_tieu_theo_danh_muc.png")
    plt.savefig(chart2, dpi=150)
    plt.show()

    # --------------------------------------------------------
    # Biểu đồ 3: Xu hướng theo tháng
    # --------------------------------------------------------

    expense_df["month"] = expense_df["date"].astype(str).str[:7]

    monthly = expense_df.groupby("month")["amount"].sum()

    plt.figure(figsize=(10, 6))

    monthly.plot(marker="o")

    plt.title("Xu hướng chi tiêu theo tháng")
    plt.xlabel("Tháng")
    plt.ylabel("Số tiền (VNĐ)")
    plt.grid(True)
    plt.tight_layout()

    chart3 = os.path.join(DATA_DIR, "03_xu_huong_chi_tieu.png")
    plt.savefig(chart3, dpi=150)
    plt.show()

    print("\n✅ Đã tạo 3 biểu đồ:")
    print(chart1)
    print(chart2)
    print(chart3)


# ============================================================
# 11. XUẤT BÁO CÁO CSV
# ============================================================

def export_report():
    """
    Xuất báo cáo tổng hợp theo danh mục thành CSV.
    """

    df = load_transactions()

    if df.empty:
        print("❌ Chưa có dữ liệu.")
        return

    expense_df = df[df["type"] == "expense"].copy()

    if expense_df.empty:
        print("❌ Chưa có khoản chi.")
        return

    report = (
        expense_df
        .groupby("category")
        .agg(
            tong_chi=("amount", "sum"),
            so_giao_dich=("amount", "count"),
            chi_trung_binh=("amount", "mean"),
        )
        .sort_values("tong_chi", ascending=False)
    )

    total = report["tong_chi"].sum()

    report["ty_trong_percent"] = (
        report["tong_chi"] / total * 100
    )

    report_file = os.path.join(DATA_DIR, "bao_cao_phan_tich.csv")

    report.to_csv(
        report_file,
        encoding="utf-8-sig"
    )

    print(f"✅ Đã xuất báo cáo: {report_file}")


# ============================================================
# 12. MENU CHÍNH
# ============================================================

def show_menu():
    """
    Hiển thị menu chính của ứng dụng.
    """

    print("\n")
    print("=" * 60)
    print("   HỆ THỐNG QUẢN LÝ CHI TIÊU CÁ NHÂN")
    print("   Phân tích thói quen tài chính")
    print("=" * 60)

    print("1. Thêm giao dịch")
    print("2. Xem giao dịch")
    print("3. Sửa giao dịch")
    print("4. Xóa giao dịch")
    print("5. Tìm kiếm giao dịch")
    print("6. Lọc giao dịch theo tháng")
    print("7. Xem tổng quan tài chính")
    print("8. Thiết lập ngân sách")
    print("9. Báo cáo ngân sách")
    print("10. Phân tích thói quen chi tiêu")
    print("11. Tạo biểu đồ")
    print("12. Xuất báo cáo CSV")
    print("0. Thoát")
    print("=" * 60)


def main():
    """
    Hàm chính điều khiển toàn bộ chương trình.
    """

    initialize_files()

    while True:

        show_menu()

        choice = input("Nhập lựa chọn: ").strip()

        if choice == "1":
            add_transaction()

        elif choice == "2":
            show_transactions()

        elif choice == "3":
            edit_transaction()

        elif choice == "4":
            delete_transaction()

        elif choice == "5":
            search_transactions()

        elif choice == "6":
            filter_by_month()

        elif choice == "7":
            financial_summary()

        elif choice == "8":
            set_budget()

        elif choice == "9":
            budget_report()

        elif choice == "10":
            spending_analysis()

        elif choice == "11":
            create_charts()

        elif choice == "12":
            export_report()

        elif choice == "0":
            print("\nCảm ơn bạn đã sử dụng chương trình!")
            break

        else:
            print("❌ Lựa chọn không hợp lệ.")


# Điểm bắt đầu của chương trình.
if __name__ == "__main__":
    main()
