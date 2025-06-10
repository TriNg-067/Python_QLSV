# Quy tắc & Luồng hoạt động module AUTH

## 1. Chức năng chính
- Đăng nhập, đăng xuất, quên mật khẩu, đặt lại mật khẩu cho user.
- Hỗ trợ phân quyền đăng nhập theo vai trò: admin, teacher, student.

## 2. Phân quyền & Kiểm tra bảo mật
- Tất cả route đều sử dụng Flask-Login để kiểm soát đăng nhập.
- Đăng nhập: Kiểm tra username, password, role. Nếu đúng, chuyển hướng theo role.
- Đăng xuất: Chỉ user đã đăng nhập mới thực hiện được.
- Quên mật khẩu: Kiểm tra tồn tại user, gửi email hoặc hiển thị link đặt lại mật khẩu.
- Đặt lại mật khẩu: Kiểm tra token hợp lệ, còn hạn mới cho phép đổi mật khẩu.
- Tất cả các form đều có CSRF token.

## 3. Các route chính
- `/auth/login`: Đăng nhập.
- `/auth/logout`: Đăng xuất.
- `/auth/forgot-password`: Quên mật khẩu.
- `/auth/reset-password/<token>`: Đặt lại mật khẩu.

## 4. Quy tắc nghiệp vụ
- Đăng nhập đúng role mới cho phép truy cập.
- Nếu sai role, báo lỗi rõ ràng.
- Nếu sai username/password, báo lỗi rõ ràng.
- Token đặt lại mật khẩu chỉ dùng một lần, có thời hạn.

## 5. Lưu ý phát triển/mở rộng
- Khi thêm role mới, cần cập nhật logic kiểm tra role ở route login.
- Khi tích hợp xác thực đa yếu tố (MFA), cần bổ sung kiểm tra ở route login.
- Đảm bảo các thông báo lỗi không tiết lộ thông tin nhạy cảm.
- Đảm bảo các email gửi đi không chứa thông tin nhạy cảm. 