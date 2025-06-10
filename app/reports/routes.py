from flask import render_template, send_file, flash, after_this_request, redirect, url_for
from flask_login import current_user, login_required
from app import app, db
from app.models import User, Class
from app.reports import reports_bp
from app.students.routes import get_filterable_students
import pandas as pd
import tempfile
import os
import traceback
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from app.rules.permissions import admin_required, teacher_required, student_required

# Helper function - tạo và gửi file tạm thời
def create_and_send_temp_file(data, file_type):
    """Tạo và gửi file tạm thời (PDF hoặc Excel)"""
    temp_filename = None
    
    try:
        if file_type == 'pdf':
            doc, elements, temp_filename = data
            # Build PDF document
            doc.build(elements)
            app.logger.info(f'Đã tạo file PDF tạm thành công: {temp_filename}')
            mime_type = 'application/pdf'
            download_name = 'danh_sach_sv.pdf'
        elif file_type == 'excel':
            df = data
            # Lưu DataFrame vào file Excel
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            temp_filename = temp_file.name
            temp_file.close()
            
            with pd.ExcelWriter(temp_filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Danh sách SV')
            
            app.logger.info(f'Đã tạo file Excel tạm thành công')
            mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            download_name = 'danh_sach_sv.xlsx'
        else:
            raise ValueError(f'Loại file không hỗ trợ: {file_type}')
        
        # Thiết lập hàm xóa file sau khi gửi
        @after_this_request
        def remove_file(response):
            try:
                if temp_filename and os.path.exists(temp_filename):
                    os.unlink(temp_filename)
                    app.logger.info(f'Đã xóa file tạm thành công')
            except Exception as e:
                app.logger.error(f'Lỗi khi xóa file tạm: {str(e)}')
            return response
        
        # Gửi file
        return send_file(
            temp_filename,
            mimetype=mime_type,
            as_attachment=True,
            download_name=download_name
        )
    except Exception as e:
        app.logger.error(f'Lỗi khi tạo và gửi file: {str(e)}')
        app.logger.error(traceback.format_exc())
        flash(f'Lỗi khi tạo và gửi file: {str(e)}', 'danger')
        return redirect(url_for('students.student_list'))

# Đăng ký font tiếng Việt cho PDF
def register_font():
    """Đăng ký font hỗ trợ tiếng Việt cho PDF"""
    try:
        # Đăng ký font DejaVuSans (hỗ trợ Unicode, bao gồm tiếng Việt)
        dejavu_sans_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'DejaVuSans.ttf')
        
        # Kiểm tra xem file font có tồn tại không
        if not os.path.exists(dejavu_sans_path):
            app.logger.error(f'Không tìm thấy file font tại: {dejavu_sans_path}')
            return False
            
        pdfmetrics.registerFont(TTFont('DejaVuSans', dejavu_sans_path))
        app.logger.info(f'Đã đăng ký font DejaVuSans thành công từ {dejavu_sans_path}')
        return True
    except Exception as e:
        app.logger.error(f'Lỗi khi đăng ký font: {str(e)}')
        app.logger.error(traceback.format_exc())
        return False

@reports_bp.route('/export-excel')
@login_required
def export_excel():
    if current_user.role not in ['admin', 'teacher']:
        flash('Bạn không có quyền xuất báo cáo.', 'danger')
        return redirect(url_for('students.student_list'))
    search = ""
    students = get_filterable_students(search)
    if not students:
        flash('Không có dữ liệu sinh viên để xuất', 'warning')
        return redirect(url_for('students.student_list'))
    data = []
    for student in students:
        data.append({
            'Mã SV': student.student_code,
            'Họ và tên': student.fullname,
            'Ngày sinh': student.birthdate.strftime('%d/%m/%Y') if student.birthdate else '',
            'Giới tính': student.gender or '',
            'Email': student.email or '',
            'Lớp': student.class_.name if student.class_ else '',
            'Điểm': student.score if student.score is not None else 'Chưa có điểm'
        })
    df = pd.DataFrame(data)
    return create_and_send_temp_file(df, 'excel')

@reports_bp.route('/export-pdf')
@login_required
def export_pdf():
    if current_user.role not in ['admin', 'teacher']:
        flash('Bạn không có quyền xuất báo cáo.', 'danger')
        return redirect(url_for('students.student_list'))
    try:
        search = ""
        students = get_filterable_students(search)
        if not students:
            flash('Không có dữ liệu sinh viên để xuất', 'warning')
            return redirect(url_for('students.student_list'))
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_filename = temp_file.name
        temp_file.close()
        font_registered = register_font()
        if not font_registered:
            flash('Không thể đăng ký font cho PDF. Sử dụng font mặc định.', 'warning')
        data = [['#', 'Mã SV', 'Họ và tên', 'Ngày sinh', 'Giới tính', 'Lớp', 'Điểm']]
        for idx, student in enumerate(students, 1):
            birthdate_str = student.birthdate.strftime('%d/%m/%Y') if student.birthdate else ''
            data.append([
                str(idx),
                student.student_code,
                student.fullname,
                birthdate_str,
                student.gender or '',
                student.class_.name if student.class_ else '',
                str(student.score) if student.score is not None else ''
            ])
        doc = SimpleDocTemplate(
            temp_filename,
            pagesize=letter,
            title="Danh sách sinh viên",
            author="Student Management System"
        )
        elements = []
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        if font_registered:
            title_style = ParagraphStyle(
                name='VietnameseTitle',
                fontName='DejaVuSans',
                fontSize=16,
                alignment=1,  # Center
                spaceAfter=12
            )
        title = Paragraph("DANH SÁCH SINH VIÊN", title_style)
        elements.append(title)
        elements.append(Paragraph("<br/>", styles['Normal']))
        
        font_name = 'DejaVuSans' if font_registered else 'Helvetica'
        table = Table(data)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), font_name),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
        table.setStyle(style)
        elements.append(table)
        elements.append(Paragraph("<br/><br/>", styles['Normal']))
        signature_style = ParagraphStyle(
            name='Signature',
            fontName=font_name,
            fontSize=10,
            alignment=2  # Right align
        )
        current_date = pd.Timestamp.now().strftime('%d/%m/%Y')
        sign_text = f"Ngày {current_date}<br/>Người xuất báo cáo<br/><br/><br/>{current_user.username}"
        elements.append(Paragraph(sign_text, signature_style))
        return create_and_send_temp_file((doc, elements, temp_filename), 'pdf')
    except Exception as e:
        app.logger.error(f'Lỗi khi tạo file PDF: {str(e)}')
        app.logger.error(traceback.format_exc())
        flash(f'Không thể tạo file PDF: {str(e)}', 'danger')
        return redirect(url_for('students.student_list'))

@reports_bp.route('/export-excel-teachers')
@login_required
@admin_required
def export_excel_teachers():
    search = ""
    # Lấy danh sách giảng viên
    query = User.query.filter_by(role='teacher')
    if search:
        query = query.filter((User.teacher_code.ilike(f'%{search}%')) | (User.fullname.ilike(f'%{search}%')))
    teachers = query.all()
    if not teachers:
        flash('Không có dữ liệu giảng viên để xuất', 'warning')
        return redirect(url_for('teachers.teacher_list'))
    data = []
    for teacher in teachers:
        data.append({
            'Mã GV': teacher.teacher_code,
            'Họ và tên': teacher.fullname,
            'Tên đăng nhập': teacher.username,
            'Email': teacher.email or '',
            'SĐT': teacher.phone or '',
            'Ngày sinh': teacher.birthdate.strftime('%d/%m/%Y') if teacher.birthdate else '',
            'Giới tính': teacher.gender or '',
            'Các lớp phụ trách': ', '.join([c.name for c in teacher.classes])
        })
    df = pd.DataFrame(data)
    # Sử dụng hàm riêng để đặt tên file cho giảng viên
    return create_and_send_temp_file_with_name(df, 'excel', 'danh_sach_giang_vien.xlsx')

@reports_bp.route('/export-pdf-teachers')
@login_required
@admin_required
def export_pdf_teachers():
    try:
        search = ""
        query = User.query.filter_by(role='teacher')
        if search:
            query = query.filter((User.teacher_code.ilike(f'%{search}%')) | (User.fullname.ilike(f'%{search}%')))
        teachers = query.all()
        if not teachers:
            flash('Không có dữ liệu giảng viên để xuất', 'warning')
            return redirect(url_for('teachers.teacher_list'))
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_filename = temp_file.name
        temp_file.close()
        font_registered = register_font()
        if not font_registered:
            flash('Không thể đăng ký font cho PDF. Sử dụng font mặc định.', 'warning')
        data = [['#<br/>STT', 'Mã GV', 'Họ và tên', 'Tên đăng nhập', 'Email', 'SĐT', 'Ngày sinh', 'Giới tính', 'Các lớp phụ trách']]

        for idx, teacher in enumerate(teachers, 1):
            birthdate_str = teacher.birthdate.strftime('%d/%m/%Y') if teacher.birthdate else ''
            data.append([
                str(idx),
                teacher.teacher_code,
                teacher.fullname,
                teacher.username,
                teacher.email or '',
                teacher.phone or '',
                birthdate_str,
                teacher.gender or '',
                ', '.join([c.name for c in teacher.classes])
            ])
        from reportlab.lib.pagesizes import letter, landscape
        doc = SimpleDocTemplate(
            temp_filename,
            pagesize=landscape(letter),
            leftMargin=72,   # 1 inch
            rightMargin=72,  # 1 inch
            topMargin=48,    # 0.67 inch
            bottomMargin=48, # 0.67 inch
            title="Danh sách giảng viên",
            author="Student Management System"
        )
        elements = []
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        if font_registered:
            title_style = ParagraphStyle(
                name='VietnameseTitle',
                fontName='DejaVuSans',
                fontSize=16,
                alignment=1,
                spaceAfter=12
            )
        title = Paragraph("DANH SÁCH GIẢNG VIÊN", title_style)
        elements.append(title)
        elements.append(Paragraph("<br/>", styles['Normal']))
        font_name = 'DejaVuSans' if font_registered else 'Helvetica'
        header_pg_style = ParagraphStyle(
            'PdfHeaderCellStyleForTeacherList',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=12,
            textColor=colors.whitesmoke,
            alignment=1,
            leading=15
        )
        header_row = [
            Paragraph('#<br/>STT', header_pg_style),
            Paragraph('Mã GV', header_pg_style),
            Paragraph('Họ và tên', header_pg_style),
            Paragraph('Tên đăng nhập', header_pg_style),
            Paragraph('Email', header_pg_style),
            Paragraph('SĐT', header_pg_style),
            Paragraph('Ngày sinh', header_pg_style),
            Paragraph('Giới tính', header_pg_style),
            Paragraph('Các lớp phụ trách', header_pg_style)
        ]
        data[0] = header_row
        col_widths = [
            35,    # STT
            55,    # Mã GV
            115,   # Họ và tên
            80,    # Tên đăng nhập
            140,   # Email
            100,    # SĐT
            80,    # Ngày sinh
            45,    # Giới tính
            95    # Các lớp phụ trách
        ]
        table = Table(data, colWidths=col_widths)
        font_name = 'DejaVuSans' if font_registered else 'Helvetica'
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), font_name),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
        table.setStyle(style)
        elements.append(table)
        elements.append(Paragraph("<br/><br/>", styles['Normal']))
        signature_style = ParagraphStyle(
            name='Signature',
            fontName=font_name,
            fontSize=10,
            alignment=2
        )
        current_date = pd.Timestamp.now().strftime('%d/%m/%Y')
        sign_text = f"Ngày {current_date}<br/>Người xuất báo cáo<br/><br/><br/>{current_user.username}"
        elements.append(Paragraph(sign_text, signature_style))
        # Sử dụng hàm riêng để đặt tên file cho giảng viên
        return create_and_send_temp_file_with_name((doc, elements, temp_filename), 'pdf', 'danh_sach_giang_vien.pdf')
    except Exception as e:
        app.logger.error(f'Lỗi khi tạo file PDF: {str(e)}')
        app.logger.error(traceback.format_exc())
        flash(f'Không thể tạo file PDF: {str(e)}', 'danger')
        return redirect(url_for('teachers.teacher_list')) 

def create_and_send_temp_file_with_name(data, file_type, custom_name):
    """Tạo và gửi file tạm thời (PDF hoặc Excel) với tên file tuỳ chỉnh"""
    temp_filename = None
    try:
        if file_type == 'pdf':
            doc, elements, temp_filename = data
            doc.build(elements)
            app.logger.info(f'Đã tạo file PDF tạm thành công: {temp_filename}')
            mime_type = 'application/pdf'
            download_name = custom_name
        elif file_type == 'excel':
            df = data
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            temp_filename = temp_file.name
            temp_file.close()
            with pd.ExcelWriter(temp_filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Danh sách GV')
            app.logger.info(f'Đã tạo file Excel tạm thành công')
            mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            download_name = custom_name
        else:
            raise ValueError(f'Loại file không hỗ trợ: {file_type}')
        @after_this_request
        def remove_file(response):
            try:
                if temp_filename and os.path.exists(temp_filename):
                    os.unlink(temp_filename)
                    app.logger.info(f'Đã xóa file tạm thành công')
            except Exception as e:
                app.logger.error(f'Lỗi khi xóa file tạm: {str(e)}')
            return response
        return send_file(
            temp_filename,
            mimetype=mime_type,
            as_attachment=True,
            download_name=download_name
        )
    except Exception as e:
        app.logger.error(f'Lỗi khi tạo và gửi file: {str(e)}')
        app.logger.error(traceback.format_exc())
        flash(f'Lỗi khi tạo và gửi file: {str(e)}', 'danger')
        return redirect(url_for('teachers.teacher_list')) 