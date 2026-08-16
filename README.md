# Hệ thống quản lý chi tiêu cá nhân và phân tích thói quen tài chính

## 1. Mục tiêu
Ứng dụng console bằng Python giúp quản lý giao dịch thu/chi, lọc dữ liệu, quản lý ngân sách, phân tích thói quen chi tiêu và tạo biểu đồ.

## 2. Cấu trúc
```text
He_thong_quan_ly_chi_tieu_Python_Final/
├── main.py              # Menu và điều phối chương trình
├── transaction.py       # CRUD, tìm kiếm, lọc nâng cao
├── storage.py           # Đọc/ghi CSV
├── analysis.py          # Tổng hợp và phân tích
├── budget.py            # Ngân sách và cảnh báo
├── visualization.py     # 3 loại biểu đồ
├── test_system.py       # Kiểm thử tự động
├── requirements.txt
├── README.md
├── data/
│   ├── transactions.csv # 120 giao dịch mô phỏng, 4 tháng
│   └── budgets.csv      # Ngân sách tháng 07/2026
├── charts/
└── screenshots/
```

## 3. Cài đặt
Sau khi tải file Project.zip trong folder Source Code
```bash
pip install -r requirements.txt
```

## 4. Chạy
```bash
python main.py
```

## 5. Chạy kiểm thử
```bash
python test_system.py
```

