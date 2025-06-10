# Quy tắc & Luồng hoạt động module TEACHERS

## 1. Chức năng chính
- Quản lý giảng viên: tạo, sửa, xóa, xem chi tiết, lọc, tìm kiếm, xuất báo cáo.

## 2. Phân quyền & Kiểm tra bảo mật
- Tất cả route đều yêu cầu đăng nhập.
- Chỉ admin mới có quyền tạo, sửa, xóa thông tin giảng viên.
- Giảng viên chỉ được phép chỉnh sửa thông tin cá nhân của mình.
- Các thao tác nhạy cảm đều kiểm tra quyền qua các hàm kiểm tra role và id.
- Các form đều có CSRF token.

## 3. Các route chính
- `/teachers/`: Danh sách giảng viên, lọc, tìm kiếm.
- `/teachers/create`: Tạo giảng viên mới (chỉ admin).
- `/teachers/<id>/edit`: Sửa thông tin giảng viên (admin hoặc chính giảng viên đó).
- `/teachers/<id>/delete`: Xóa giảng viên (chỉ admin).
- `/teachers/<id>`: Xem chi tiết giảng viên.

## 4. Quy tắc nghiệp vụ
- Khi tạo/sửa giảng viên, kiểm tra trùng mã, username, email.
- Khi xóa, chỉ admin mới được phép thực hiện.
- Các nút thao tác trên UI chỉ hiển thị nếu user có quyền phù hợp.

## 5. Lưu ý phát triển/mở rộng
- Khi thêm trường thông tin mới cho giảng viên, cần cập nhật form và kiểm tra hợp lệ.
- Khi thay đổi logic phân quyền, cần cập nhật các hàm kiểm tra quyền tương ứng.
- Đảm bảo các thao tác xóa là "soft delete" nếu cần lưu lịch sử. 