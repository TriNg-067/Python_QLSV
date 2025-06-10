# Quy tắc & Luồng hoạt động liên quan đến quyền trong MODELS

## 1. Các role hợp lệ
- `admin`: Quản trị viên toàn hệ thống, có toàn quyền thao tác.
- `teacher`: Giảng viên/Chuyên viên, chỉ thao tác với sinh viên/lớp mình phụ trách.
- `student`: Sinh viên, chỉ xem và chỉnh sửa thông tin cá nhân.

## 2. Các hàm nghiệp vụ phân quyền
- `get_assigned_classes()`: Trả về danh sách lớp mà giảng viên được phân công (nếu có).
- `can_manage_class(class_name)`: Trả về True nếu user là admin hoặc là teacher được phân công lớp đó.
- `can_manage_student(student)`: Trả về True nếu user là admin hoặc là teacher phụ trách lớp của student.

## 3. Ứng dụng trong các module khác
- Các hàm này được sử dụng để kiểm tra quyền thao tác với sinh viên/lớp học trong students/routes.py, teachers/routes.py và các nơi khác.
- Đảm bảo mọi thao tác nhạy cảm đều kiểm tra quyền qua các hàm này.

## 4. Quy tắc chứng nhận (Certificate)
- Chỉ sinh viên có điểm số >= 8.0 mới được xem chứng nhận.
- Chỉ admin, teacher quản lý lớp hoặc chính sinh viên đó mới được xem chứng nhận.

## 5. Lưu ý phát triển/mở rộng
- Khi thêm role mới, cần cập nhật các hàm kiểm tra quyền tương ứng.
- Khi thay đổi logic phân quyền, cần cập nhật lại các hàm nghiệp vụ này. 