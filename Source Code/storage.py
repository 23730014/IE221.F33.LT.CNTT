"""Module lưu trữ dữ liệu cho hệ thống quản lý chi tiêu.

Nhiệm vụ chính:
- Xác định vị trí các file CSV.
- Khởi tạo file nếu chưa tồn tại.
- Đọc dữ liệu từ CSV thành pandas.DataFrame.
- Ghi DataFrame trở lại CSV.

Tách phần lưu trữ thành module riêng giúp các module khác không phải
quan tâm đến đường dẫn file và cách mã hóa CSV.
"""
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TRANSACTION_FILE = DATA_DIR / "transactions.csv"
BUDGET_FILE = DATA_DIR / "budgets.csv"

TRANSACTION_FIELDS = ["id", "date", "type", "category", "amount", "description"]
BUDGET_FIELDS = ["month", "category", "limit"]


def initialize_files():
    """Tạo thư mục/file dữ liệu nếu chúng chưa tồn tại."""
    DATA_DIR.mkdir(exist_ok=True)

    if not TRANSACTION_FILE.exists():
        pd.DataFrame(columns=TRANSACTION_FIELDS).to_csv(
            TRANSACTION_FILE, index=False, encoding="utf-8-sig"
        )

    if not BUDGET_FILE.exists():
        pd.DataFrame(columns=BUDGET_FIELDS).to_csv(
            BUDGET_FILE, index=False, encoding="utf-8-sig"
        )


def load_transactions():
    """Đọc transactions.csv và chuẩn hóa kiểu dữ liệu."""
    initialize_files()
    try:
        df = pd.read_csv(TRANSACTION_FILE, encoding="utf-8-sig")
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=TRANSACTION_FIELDS)

    if df.empty:
        return pd.DataFrame(columns=TRANSACTION_FIELDS)

    df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    return df


def save_transactions(df):
    """Ghi danh sách giao dịch vào CSV."""
    df.to_csv(TRANSACTION_FILE, index=False, encoding="utf-8-sig")


def load_budgets():
    """Đọc budgets.csv và chuẩn hóa cột hạn mức."""
    initialize_files()
    try:
        df = pd.read_csv(BUDGET_FILE, encoding="utf-8-sig")
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=BUDGET_FIELDS)

    if df.empty:
        return pd.DataFrame(columns=BUDGET_FIELDS)

    df["limit"] = pd.to_numeric(df["limit"], errors="coerce").fillna(0.0)
    return df


def save_budgets(df):
    """Ghi ngân sách vào CSV."""
    df.to_csv(BUDGET_FILE, index=False, encoding="utf-8-sig")
