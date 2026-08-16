"""Quản lý giao dịch: thêm, sửa, xóa, tìm kiếm và lọc nâng cao."""
from datetime import datetime
import pandas as pd
from storage import load_transactions, save_transactions

CATEGORIES = [
    "Ăn uống", "Đi lại", "Mua sắm", "Học tập",
    "Giải trí", "Hóa đơn", "Y tế", "Khác"
]
TRANSACTION_TYPES = ["income", "expense"]


def format_money(value):
    """Định dạng số tiền theo cách dễ đọc."""
    return f"{float(value):,.0f} đ"


def validate_date(date_text):
    """Kiểm tra ngày theo định dạng YYYY-MM-DD."""
    try:
        datetime.strptime(str(date_text), "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Ngày phải có định dạng YYYY-MM-DD.") from exc


def validate_month(month_text):
    """Kiểm tra tháng theo định dạng YYYY-MM."""
    try:
        datetime.strptime(f"{month_text}-01", "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Tháng phải có định dạng YYYY-MM.") from exc


def validate_transaction(kind, category, amount):
    """Kiểm tra loại, danh mục và số tiền của giao dịch."""
    if kind not in TRANSACTION_TYPES:
        raise ValueError("Loại giao dịch chỉ nhận income hoặc expense.")
    if category not in CATEGORIES:
        raise ValueError("Danh mục không hợp lệ.")
    if float(amount) <= 0:
        raise ValueError("Số tiền phải lớn hơn 0.")


def next_id(df):
    """Sinh mã giao dịch mới bằng ID lớn nhất hiện có + 1."""
    if df.empty:
        return 1
    return int(df["id"].dropna().max()) + 1


def add_transaction(date, kind, category, amount, description=""):
    """Thêm một giao dịch mới và lưu xuống CSV."""
    validate_date(date)
    validate_transaction(kind, category, amount)
    df = load_transactions()

    row = {
        "id": next_id(df),
        "date": date,
        "type": kind,
        "category": category,
        "amount": float(amount),
        "description": description,
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_transactions(df)
    return row


def edit_transaction(transaction_id, date, kind, category, amount, description=""):
    """Sửa giao dịch theo ID."""
    validate_date(date)
    validate_transaction(kind, category, amount)
    df = load_transactions()
    mask = df["id"].astype(int) == int(transaction_id)

    if not mask.any():
        raise KeyError("Không tìm thấy giao dịch cần sửa.")

    index = df.index[mask][0]
    df.loc[index, ["date", "type", "category", "amount", "description"]] = [
        date, kind, category, float(amount), description
    ]
    save_transactions(df)


def delete_transaction(transaction_id):
    """Xóa giao dịch theo ID."""
    df = load_transactions()
    mask = df["id"].astype(int) == int(transaction_id)

    if not mask.any():
        raise KeyError("Không tìm thấy giao dịch cần xóa.")

    save_transactions(df.loc[~mask].copy())


def search_transactions(keyword):
    """Tìm kiếm theo từ khóa trong toàn bộ các cột."""
    df = load_transactions()
    if df.empty:
        return df

    keyword = str(keyword).lower()
    mask = df.astype(str).apply(
        lambda column: column.str.lower().str.contains(keyword, regex=False)
    ).any(axis=1)
    return df[mask].copy()


def filter_transactions(
    start_date=None,
    end_date=None,
    kind=None,
    category=None,
    min_amount=None,
    max_amount=None,
):
    """Lọc nâng cao theo ngày, loại, danh mục và khoảng tiền."""
    df = load_transactions()
    if df.empty:
        return df

    result = df.copy()
    result["date_dt"] = pd.to_datetime(result["date"], errors="coerce")

    if start_date:
        validate_date(start_date)
        result = result[result["date_dt"] >= pd.to_datetime(start_date)]
    if end_date:
        validate_date(end_date)
        result = result[result["date_dt"] <= pd.to_datetime(end_date)]
    if start_date and end_date and start_date > end_date:
        raise ValueError("Ngày bắt đầu không được sau ngày kết thúc.")
    if kind:
        if kind not in TRANSACTION_TYPES:
            raise ValueError("Loại giao dịch không hợp lệ.")
        result = result[result["type"] == kind]
    if category:
        if category not in CATEGORIES:
            raise ValueError("Danh mục không hợp lệ.")
        result = result[result["category"] == category]
    if min_amount is not None:
        if float(min_amount) < 0:
            raise ValueError("Số tiền tối thiểu không được âm.")
        result = result[result["amount"] >= float(min_amount)]
    if max_amount is not None:
        if float(max_amount) < 0:
            raise ValueError("Số tiền tối đa không được âm.")
        result = result[result["amount"] <= float(max_amount)]
    if min_amount is not None and max_amount is not None and float(min_amount) > float(max_amount):
        raise ValueError("Số tiền tối thiểu không được lớn hơn số tiền tối đa.")

    return result.drop(columns=["date_dt"])
