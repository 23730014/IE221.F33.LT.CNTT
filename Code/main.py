"""Ứng dụng console chính của hệ thống quản lý chi tiêu cá nhân.

Chạy chương trình bằng:
    python main.py

Các chức năng chính:
1. CRUD giao dịch.
2. Tìm kiếm và lọc nâng cao.
3. Tổng quan tài chính.
4. Quản lý ngân sách và cảnh báo.
5. Phân tích thói quen chi tiêu.
6. Trực quan hóa bằng 3 loại biểu đồ.
"""
from analysis import financial_summary, spending_analysis
from budget import budget_report, set_budget
from storage import initialize_files, load_transactions
from transaction import (
    CATEGORIES,
    add_transaction,
    delete_transaction,
    edit_transaction,
    filter_transactions,
    format_money,
    search_transactions,
)
from visualization import create_charts


def show_dataframe(df):
    """Hiển thị DataFrame theo định dạng thân thiện với người dùng."""
    if df.empty:
        print("Chưa có dữ liệu phù hợp.")
        return

    display = df.copy()
    if "type" in display.columns:
        display["type"] = display["type"].map({"income": "Thu", "expense": "Chi"})
    if "amount" in display.columns:
        display["amount"] = display["amount"].apply(format_money)
    print(display.to_string(index=False))


def prompt_category():
    """Cho người dùng chọn danh mục từ danh sách chuẩn."""
    print("Danh mục:")
    for index, category in enumerate(CATEGORIES, start=1):
        print(f"  {index}. {category}")

    while True:
        try:
            choice = int(input("Chọn danh mục: "))
            if 1 <= choice <= len(CATEGORIES):
                return CATEGORIES[choice - 1]
        except ValueError:
            pass
        print("Lựa chọn không hợp lệ.")


def prompt_type():
    """Cho người dùng chọn income hoặc expense."""
    while True:
        print("1. income - Thu nhập")
        print("2. expense - Chi tiêu")
        choice = input("Chọn loại: ").strip()
        if choice == "1":
            return "income"
        if choice == "2":
            return "expense"
        print("Lựa chọn không hợp lệ.")


def menu():
    """In menu chính."""
    print("\n" + "=" * 66)
    print(" HỆ THỐNG QUẢN LÝ CHI TIÊU CÁ NHÂN")
    print(" Phân tích thói quen tài chính")
    print("=" * 66)
    items = [
        "Thêm giao dịch",
        "Xem giao dịch",
        "Sửa giao dịch",
        "Xóa giao dịch",
        "Tìm kiếm",
        "Lọc nâng cao",
        "Tổng quan tài chính",
        "Thiết lập ngân sách",
        "Báo cáo ngân sách",
        "Phân tích thói quen chi tiêu",
        "Tạo biểu đồ",
        "Thoát",
    ]
    for index, item in enumerate(items, start=1):
        print(f"{index:>2}. {item}")


def add_flow():
    """Luồng nhập một giao dịch mới."""
    date = input("Ngày YYYY-MM-DD: ").strip()
    kind = prompt_type()
    category = prompt_category()
    amount = float(input("Số tiền: "))
    description = input("Mô tả: ").strip()
    row = add_transaction(date, kind, category, amount, description)
    print(f"Đã thêm giao dịch ID={row['id']}.")


def edit_flow():
    """Luồng sửa giao dịch."""
    transaction_id = int(input("ID cần sửa: "))
    date = input("Ngày YYYY-MM-DD: ").strip()
    kind = prompt_type()
    category = prompt_category()
    amount = float(input("Số tiền mới: "))
    description = input("Mô tả mới: ").strip()
    edit_transaction(transaction_id, date, kind, category, amount, description)
    print("Đã cập nhật giao dịch.")


def advanced_filter_flow():
    """Luồng lọc theo nhiều điều kiện; để trống nếu không dùng điều kiện."""
    start = input("Từ ngày YYYY-MM-DD: ").strip() or None
    end = input("Đến ngày YYYY-MM-DD: ").strip() or None
    type_text = input("Loại [income/expense]: ").strip() or None
    category = input("Danh mục (nhập đúng tên): ").strip() or None
    min_text = input("Số tiền tối thiểu: ").strip()
    max_text = input("Số tiền tối đa: ").strip()

    result = filter_transactions(
        start_date=start,
        end_date=end,
        kind=type_text,
        category=category,
        min_amount=float(min_text) if min_text else None,
        max_amount=float(max_text) if max_text else None,
    )
    print(f"Số bản ghi sau lọc: {len(result)}")
    show_dataframe(result)


def run():
    """Điểm vào chính của chương trình."""
    initialize_files()

    while True:
        menu()
        choice = input("Chọn chức năng: ").strip()

        try:
            if choice == "1":
                add_flow()
            elif choice == "2":
                show_dataframe(load_transactions())
            elif choice == "3":
                edit_flow()
            elif choice == "4":
                delete_transaction(int(input("ID cần xóa: ")))
                print("Đã xóa giao dịch.")
            elif choice == "5":
                show_dataframe(search_transactions(input("Từ khóa: ")))
            elif choice == "6":
                advanced_filter_flow()
            elif choice == "7":
                summary = financial_summary()
                print("\nTỔNG QUAN TÀI CHÍNH")
                print(f"Tổng thu      : {format_money(summary['income'])}")
                print(f"Tổng chi      : {format_money(summary['expense'])}")
                print(f"Số dư         : {format_money(summary['balance'])}")
                print(f"Số giao dịch  : {summary['transactions']}")
            elif choice == "8":
                month = input("Tháng YYYY-MM: ").strip()
                category = prompt_category()
                limit = float(input("Ngân sách: "))
                set_budget(month, category, limit)
                print("Đã lưu ngân sách.")
            elif choice == "9":
                month = input("Tháng YYYY-MM: ").strip()
                report = budget_report(month)
                show_dataframe(report)
            elif choice == "10":
                result = spending_analysis()
                print(f"\nTổng chi: {format_money(result['total_expense'])}")
                print(f"Chi trung bình/giao dịch: {format_money(result['average_expense'])}")
                print(f"Danh mục chi nhiều nhất: {result['top_category']}")
                table = result["by_category"].copy()
                table["total"] = table["total"].apply(format_money)
                table["percent"] = table["percent"].map(lambda x: f"{x:.1f}%")
                print(table.to_string(index=False))
            elif choice == "11":
                paths = create_charts()
                if not paths:
                    print("Chưa có dữ liệu chi tiêu để tạo biểu đồ.")
                else:
                    print("Đã tạo các biểu đồ:")
                    for path in paths:
                        print(path)
            elif choice == "12":
                print("Kết thúc chương trình.")
                break
            else:
                print("Lựa chọn không hợp lệ.")
        except (ValueError, KeyError) as exc:
            print(f"Lỗi dữ liệu: {exc}")
        except Exception as exc:
            print(f"Lỗi hệ thống: {exc}")


if __name__ == "__main__":
    run()
