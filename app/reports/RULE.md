# Quy tắc & Luồng hoạt động module REPORTS

## 1. Chức năng chính
- Xuất báo cáo danh sách sinh viên, giảng viên ra file Excel/PDF.
- Hỗ trợ lọc, tìm kiếm, thống kê trước khi xuất báo cáo.

## 2. Phân quyền & Kiểm tra bảo mật
- Tất cả route xuất file đều yêu cầu đăng nhập.
- Chỉ admin và teacher mới có quyền xuất báo cáo.
- Student KHÔNG được phép xuất bất kỳ dữ liệu báo cáo nào.
- Kiểm tra quyền trước khi thực hiện xuất file.
- Các file tạm được xóa tự động sau khi xuất.

## 3. Các route chính
- `/reports/export-excel`: Xuất danh sách sinh viên ra Excel.
- `/reports/export-pdf`: Xuất danh sách sinh viên ra PDF.
- `/reports/export-pdf-teachers`: Xuất danh sách giảng viên ra PDF.

## 4. Quy tắc nghiệp vụ
- Khi xuất file, kiểm tra quyền và lọc dữ liệu phù hợp với user hiện tại.
- Nếu không có dữ liệu phù hợp, báo lỗi.
- Khi xuất PDF, đăng ký font hỗ trợ tiếng Việt nếu có.
- Dữ liệu xuất gồm: Mã SV/Mã GV, Họ và tên, Ngày sinh, Giới tính, Lớp, Điểm, Các lớp phụ trách (nếu có).

## 5. Lưu ý phát triển/mở rộng
- Khi thêm trường dữ liệu mới, cần cập nhật logic xuất file.
- Đảm bảo các file tạm được xóa đúng cách, tránh rò rỉ dữ liệu.
- Đảm bảo không xuất dữ liệu nhạy cảm không cần thiết. 