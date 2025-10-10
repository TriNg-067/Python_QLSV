## Mục đích
Ứng dụng quản lý sinh viên, giáo viên, lớp học, báo cáo, xuất file PDF/Excel, xác thực, gửi mail, v.v.

---

## Hình ảnh Demo
![Giaodien_Dashboard](https://github.com/user-attachments/assets/69067d22-ff45-4861-a597-5dbdfbd88a35)

[Xem thêm tại đây](https://drive.google.com/drive/folders/1nHXQ1bWaEwojZP1lxT9QQT4jBCYwNH0h?usp=drive_link)
---

## Cây thư mục & Mô tả

```
QLSV-Python/
│
├── app/                        # Thư mục chính chứa code ứng dụng
│   ├── __init__.py             # Khởi tạo Flask app, đăng ký blueprint, cấu hình
│   ├── forms.py                # Định nghĩa các form WTForms dùng chung
│   ├── models.py               # Định nghĩa các model SQLAlchemy
│   ├── auth/                   # Xác thực người dùng (login, logout, quên mật khẩu)
│   │   ├── routes.py           # Xử lý route xác thực
│   │   ├── forms.py            # Form xác thực
│   │   └── RULE.md             # Quy tắc module auth
│   ├── classes/                # Quản lý lớp học
│   │   ├── routes.py           # Route lớp học
│   │   └── __init__.py         # Khởi tạo module classes
│   ├── reports/                # Báo cáo, xuất file PDF/Excel
│   │   ├── routes.py           # Route báo cáo
│   │   ├── __init__.py         # Khởi tạo module reports
│   │   └── RULE.md             # Quy tắc module reports
│   ├── rules/                  # Quy tắc, phân quyền, validation
│   │   ├── permissions.py      # Định nghĩa quyền truy cập
│   │   └── RULE.md             # Quy tắc module rules
│   ├── students/               # Quản lý sinh viên
│   │   ├── routes.py           # Route sinh viên
│   │   ├── __init__.py         # Khởi tạo module students
│   │   └── RULE.md             # Quy tắc module students
│   ├── teachers/               # Quản lý giáo viên
│   │   ├── routes.py           # Route giáo viên
│   │   ├── __init__.py         # Khởi tạo module teachers
│   │   └── RULE.md             # Quy tắc module teachers
│   ├── static/                 # Tài nguyên tĩnh (CSS, ảnh)
│   │   ├── css/
│   │   │   └── styles.css      # File CSS chính
│   │   └── img/
│   │       └── certificates/
│   │           └── Certificate.png # Ảnh mẫu chứng chỉ
│   └── templates/              # HTML template (Jinja2)
│       ├── base.html           # Template cơ sở
│       ├── index.html          # Trang chủ
│       ├── 500.html            # Trang lỗi
│       ├── includes/
│       │   └── navbar.html     # Thanh điều hướng dùng chung
│       ├── auth/               # Template xác thực
│       │   ├── login.html
│       │   ├── forgot_password.html
│       │   ├── reset_password.html
│       │   └── change_password.html
│       ├── students/           # Template sinh viên
│       │   ├── index.html
│       │   ├── statistics.html
│       │   ├── edit.html
│       │   ├── create.html
│       │   ├── view.html
│       │   └── certificate.html
│       ├── teachers/           # Template giáo viên
│       │   ├── index.html
│       │   ├── edit_teacher.html
│       │   ├── create_teacher.html
│       │   └── edit_profile.html
│       └── classes/            # Template lớp học
│           ├── index.html
│           └── create_edit.html
│
├── config.py                   # File cấu hình Flask (DB URI, secret key, ...)
├── run.py                      # Entry point khởi động app Flask
├── requirements.txt            # Danh sách thư viện Python cần cài
├── DejaVuSans.ttf              # Font chữ dùng cho xuất PDF
├── instance/
│   └── students.db             # File SQLite database
├── migrations/                 # Quản lý migration cho database
│   ├── env.py                  # Script môi trường Alembic
│   ├── alembic.ini             # Cấu hình Alembic
│   ├── script.py.mako          # Template script migration
│   └── versions/               # Các file migration
└── .gitignore                  # File/thư mục bị git bỏ qua
```

---

## Framework, Công nghệ, Thư viện sử dụng

- **Flask**: Web framework chính
- **Flask-SQLAlchemy**: ORM cho database
- **Flask-WTF, WTForms**: Xử lý form, validation
- **Flask-Login**: Quản lý đăng nhập, session
- **Flask-Mail**: Gửi email
- **Flask-Migrate, Alembic**: Migration cho database
- **SQLAlchemy**: ORM core
- **python-dotenv**: Đọc biến môi trường từ file .env
- **pandas**: Xử lý dữ liệu, xuất/nhập file Excel
- **openpyxl**: Đọc/ghi file Excel (.xlsx)
- **reportlab**: Tạo file PDF
- **itsdangerous, werkzeug**: Bảo mật, session, hash, v.v.

---

## Database

- **SQLite** (file: `instance/students.db`)
  - Đơn giản, dễ triển khai, phù hợp cho ứng dụng nhỏ hoặc demo.
  - Có thể chuyển sang các hệ quản trị khác (MySQL, PostgreSQL) nếu cần.

---

## Hướng dẫn cài đặt

1. **Clone project:**
   ```bash
   git clone <repo-url>
   cd QLSV-Python
   ```
2. **Tạo virtualenv (khuyến nghị):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Cài đặt thư viện:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Cấu hình môi trường:**
   - Tạo file `.env` (nếu cần), ví dụ:
     ```env
     FLASK_APP=run.py
     FLASK_ENV=development
     SECRET_KEY=your_secret_key
     SQLALCHEMY_DATABASE_URI=sqlite:///instance/students.db
     MAIL_SERVER=smtp.gmail.com
     MAIL_PORT=587
     MAIL_USE_TLS=1
     MAIL_USERNAME=your_email
     MAIL_PASSWORD=your_password
     ```
5. **Khởi tạo database (nếu chưa có):**
   ```bash
   flask db upgrade
   ```
6. **Chạy ứng dụng:**
   ```bash
   flask run
   ```
   hoặc
   ```bash
   python run.py
   ```

---

## Một số module chính

- **auth**: Đăng nhập, đăng xuất, đổi/quên mật khẩu, xác thực người dùng
- **students**: Quản lý sinh viên, thống kê, xuất chứng chỉ
- **teachers**: Quản lý giáo viên, chỉnh sửa hồ sơ
- **classes**: Quản lý lớp học
- **reports**: Xuất báo cáo, file PDF/Excel
- **rules**: Phân quyền, kiểm soát truy cập

---


## Liên hệ
- Nếu có vấn đề, liên hệ qua email (tri.np0607@gmail.com). 
