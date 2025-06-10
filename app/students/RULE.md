# Quy tắc & Luồng hoạt động module STUDENTS

## 1. Chức năng chính
- Quản lý sinh viên: tạo, sửa, xóa, xem chi tiết, lọc, tìm kiếm, thống kê, xuất báo cáo, xem giấy chứng nhận.

## 2. Phân quyền & Kiểm tra bảo mật
- Tất cả route đều yêu cầu đăng nhập.
- Chỉ admin và teacher mới có quyền tạo, sửa, xóa sinh viên.
- Teacher chỉ thao tác với sinh viên thuộc lớp mình phụ trách.
- Student chỉ xem được thông tin của chính mình.
- Các thao tác nhạy cảm đều kiểm tra quyền qua các hàm can_manage_student, can_view_student.
- Các form đều có CSRF token.

## 3. Các route chính
- `/students/`: Danh sách sinh viên, lọc, tìm kiếm, thống kê.
- `/students/create`: Tạo sinh viên mới.
- `/students/<id>/edit`: Sửa thông tin sinh viên.
- `/students/<id>/delete`: Xóa sinh viên.
- `/students/<id>`: Xem chi tiết sinh viên.
- `/students/<id>/certificate`: Xem giấy chứng nhận.

## 4. Quy tắc nghiệp vụ
- Khi tạo/sửa sinh viên, kiểm tra trùng mã, username, email.
- Khi thao tác với sinh viên, kiểm tra quyền với lớp tương ứng.
- Chỉ sinh viên có điểm >= 8.0 mới được xem giấy chứng nhận.
- Chỉ admin, teacher phụ trách hoặc chính sinh viên đó mới được xem giấy chứng nhận.
- Khi vào trang giấy chứng nhận, chỉ hiển thị nút "Quay lại danh sách".

## 5. Lưu ý phát triển/mở rộng
- Khi thêm trường thông tin mới cho sinh viên, cần cập nhật form và kiểm tra hợp lệ.
- Khi thay đổi logic phân quyền, cần cập nhật các hàm kiểm tra quyền tương ứng.
- Đảm bảo các thao tác xóa là "soft delete" nếu cần lưu lịch sử. 