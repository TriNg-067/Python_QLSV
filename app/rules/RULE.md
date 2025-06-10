# Quy tắc & Luồng hoạt động module RULES

## 1. Chức năng chính
- Cung cấp các decorator phân quyền cho toàn bộ hệ thống: @admin_required, @teacher_required, @student_required.

## 2. Decorator phân quyền
- `@admin_required`: Chỉ cho phép user role 'admin' truy cập route.
- `@teacher_required`: Chỉ cho phép user role 'teacher' truy cập route.
- `@student_required`: Chỉ cho phép user role 'student' truy cập route.
- Nếu không đủ quyền, chuyển hướng về trang chủ và hiển thị thông báo lỗi.
- Nên kết hợp với `@login_required` để đảm bảo user đã đăng nhập.

## 3. Cách sử dụng
- Import decorator vào các route cần kiểm soát quyền truy cập.
- Đặt decorator phía trên các route cần bảo vệ.

## 4. Lưu ý bảo mật
- Không nên lồng nhiều decorator phân quyền trên cùng một route.
- Đảm bảo các decorator luôn kiểm tra trạng thái đăng nhập trước khi kiểm tra role.
- Thông báo lỗi không tiết lộ thông tin nhạy cảm.

## 5. Lưu ý phát triển/mở rộng
- Khi thêm role mới, cần bổ sung decorator tương ứng.
- Khi thay đổi logic phân quyền, cần cập nhật lại decorator và các route sử dụng. 