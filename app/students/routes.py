from flask import render_template, request, redirect, url_for, flash, abort, send_file
from flask_login import current_user, login_required
from app import app, db
from app.models import User, Class
from app.forms import StudentForm
from app.students import students_bp
from collections import defaultdict
from app.rules.permissions import admin_required, teacher_required, student_required
from datetime import datetime

# Helper function - lấy sinh viên có lọc
def get_filterable_students(search_term):
    query = User.query.filter_by(role='student')
    if search_term:
        query = query.filter(
            (User.student_code.ilike(f'%{search_term}%')) |
            (User.fullname.ilike(f'%{search_term}%'))
        )
    if current_user.role == 'teacher':
        assigned_class_ids = [c.id for c in current_user.classes]
        if assigned_class_ids:
            query = query.filter(User.class_id.in_(assigned_class_ids))
        else:
            return []
    students = query.order_by(User.student_code).all()
    return students

# Helper function - kiểm tra quyền quản lý sinh viên
def can_manage_student(student):
    if current_user.role == 'admin':
        return True
    if current_user.role == 'teacher':
        return student.class_id in [c.id for c in current_user.classes]
    return False

# Helper function - kiểm tra quyền xem sinh viên
def can_view_student(student):
    if current_user.role in ['admin', 'teacher']:
        return True
    if current_user.role == 'student':
        return current_user.id == student.id
    return False

@students_bp.route('/statistics')
@login_required
def student_statistics():
    if current_user.role == 'student':
        flash('Bạn không có quyền xem thống kê sinh viên', 'danger')
        return redirect(url_for('students.student_list'))
    students = []
    teacher_class_count = None
    if current_user.role == 'admin':
        students = User.query.filter_by(role='student').all()
    elif current_user.role == 'teacher':
        teacher_class_count = len(current_user.classes)
        assigned_class_ids = [c.id for c in current_user.classes]
        if assigned_class_ids:
            students = User.query.filter_by(role='student').filter(User.class_id.in_(assigned_class_ids)).all()
    class_stats = defaultdict(int)
    class_scores = defaultdict(list)
    gender_stats = defaultdict(int)
    gender_scores = defaultdict(list)
    grade_stats = defaultdict(int)
    score_ranges = defaultdict(int)
    total_students = len(students)
    avg_score_total = 0
    if students:
        valid_scores = []
        for student in students:
            class_name = student.class_.name if student.class_ else 'Chưa phân lớp'
            class_stats[class_name] += 1
            if student.score is not None:
                class_scores[class_name].append(student.score)
                valid_scores.append(student.score)
            gender = student.gender or 'Không xác định'
            gender_stats[gender] += 1
            if student.score is not None:
                gender_scores[gender].append(student.score)
                if student.score >= 8.0:
                    grade_stats['Giỏi'] += 1
                elif student.score >= 7.0:
                    grade_stats['Khá'] += 1
                elif student.score >= 5.5:
                    grade_stats['Trung bình'] += 1
                elif student.score >= 4.0:
                    grade_stats['Yếu'] += 1
                else:
                    grade_stats['Kém'] += 1
                if student.score >= 8.0:
                    score_ranges['8.0-10'] += 1
                elif student.score >= 7.0:
                    score_ranges['7.0-8.5'] += 1
                elif student.score >= 5.5:
                    score_ranges['5.5-7.0'] += 1
                elif student.score >= 4.0:
                    score_ranges['4.0-5.5'] += 1
                else:
                    score_ranges['0-4.0'] += 1
            else:
                grade_stats['Chưa có điểm'] += 1
                score_ranges['Chưa có điểm'] += 1
        avg_scores_by_class = {}
        for class_name, scores in class_scores.items():
            avg_scores_by_class[class_name] = round(sum(scores) / len(scores), 1) if scores else 0
        avg_scores_by_gender = {}
        for gender, scores in gender_scores.items():
            avg_scores_by_gender[gender] = round(sum(scores) / len(scores), 1) if scores else 0
        avg_score_total = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else 0
    from app.models import Class
    total_classes = Class.query.count()
    return render_template('students/statistics.html',
                           total_students=total_students,
                           avg_score_total=avg_score_total,
                           class_stats=class_stats,
                           avg_scores_by_class=avg_scores_by_class,
                           gender_stats=gender_stats,
                           avg_scores_by_gender=avg_scores_by_gender,
                           grade_stats=grade_stats,
                           score_ranges=score_ranges,
                           total_classes=total_classes,
                           is_admin=(current_user.role == 'admin'),
                           teacher_class_count=teacher_class_count
                           )

@students_bp.route('/')
@students_bp.route('/list')
@login_required
def student_list():
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'student_code')
    sort_order = request.args.get('sort_order', 'asc')
    page = int(request.args.get('page', 1))
    per_page = 15
    students = get_filterable_students(search)
    if sort_by == 'student_code':
        students = sorted(students, key=lambda x: x.student_code, reverse=(sort_order == 'desc'))
    elif sort_by == 'fullname':
        students = sorted(students, key=lambda x: x.fullname, reverse=(sort_order == 'desc'))
    elif sort_by == 'class_name':
        students = sorted(students, key=lambda x: x.class_.name if x.class_ else '', reverse=(sort_order == 'desc'))
    elif sort_by == 'score':
        students = sorted(students, key=lambda x: x.score if x.score is not None else -1, reverse=(sort_order == 'desc'))
    unique_classes = set(student.class_.name for student in students if student.class_)
    can_create = current_user.role in ['admin', 'teacher']
    if current_user.role == 'student':
        students = [current_user]
        total_pages = 1
        students_page = students
    else:
        total = len(students)
        total_pages = (total + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page
        students_page = students[start:end]
    return render_template('students/index.html', 
                        students=students_page, 
                        search=search,
                        sort_by=sort_by,
                        sort_order=sort_order,
                        unique_classes=unique_classes,
                        can_create=can_create,
                        page=page,
                        total_pages=total_pages)

@students_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_student():
    form = StudentForm()
    if form.validate_on_submit():
        if not form.password.data:
            flash('Bạn phải nhập mật khẩu cho sinh viên.', 'danger')
            return render_template('students/create.html', form=form)
        # Kiểm tra username và student_code đã tồn tại chưa
        if User.query.filter_by(username=form.username.data).first():
            flash('Tên đăng nhập này đã tồn tại. Vui lòng chọn tên khác.', 'danger')
            return render_template('students/create.html', form=form)
        if User.query.filter_by(student_code=form.student_code.data).first():
            flash('Mã sinh viên này đã tồn tại. Vui lòng chọn mã khác.', 'danger')
            return render_template('students/create.html', form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash('Email này đã tồn tại. Vui lòng chọn email khác.', 'danger')
            return render_template('students/create.html', form=form)
        student = User(
            username=form.username.data,
            role='student',
            student_code=form.student_code.data,
            fullname=form.fullname.data,
            birthdate=form.birthdate.data,
            gender=form.gender.data,
            email=form.email.data,
            class_id=form.class_id.data,
            score=form.score.data,
            avatar=form.avatar.data
        )
        student.set_password(form.password.data)
        if current_user.role == 'teacher' and student.class_id not in [c.id for c in current_user.classes]:
            flash(f'Bạn không được phép thêm sinh viên vào lớp này', 'danger')
            return render_template('students/create.html', form=form)
        db.session.add(student)
        db.session.commit()
        flash(f'Đã thêm sinh viên {student.fullname} thành công', 'success')
        return redirect(url_for('students.student_list'))
    return render_template('students/create.html', form=form)

@students_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    student = User.query.filter_by(id=id, role='student').first_or_404()
    if not can_manage_student(student):
        flash('Bạn không có quyền sửa thông tin sinh viên này', 'danger')
        return redirect(url_for('students.student_list'))
    form = StudentForm(obj=student)
    form.student_id = student.id
    if form.validate_on_submit():
        if current_user.role == 'teacher' and form.class_id.data not in [c.id for c in current_user.classes]:
            flash(f'Bạn không được phép chuyển sinh viên sang lớp này', 'danger')
            return render_template('students/edit.html', form=form, student=student)
        student.student_code = form.student_code.data
        student.fullname = form.fullname.data
        student.birthdate = form.birthdate.data
        student.gender = form.gender.data
        student.email = form.email.data
        student.class_id = form.class_id.data
        student.score = form.score.data
        student.avatar = form.avatar.data
        if form.password.data:
            student.set_password(form.password.data)
        db.session.commit()
        flash(f'Đã cập nhật thông tin sinh viên {student.fullname} thành công', 'success')
        return redirect(url_for('students.student_list'))
    return render_template('students/edit.html', form=form, student=student)

@students_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_student(id):
    student = User.query.filter_by(id=id, role='student').first_or_404()
    if not can_manage_student(student):
        flash('Bạn không có quyền xóa sinh viên này', 'danger')
        return redirect(url_for('students.student_list'))
    fullname = student.fullname
    db.session.delete(student)
    db.session.commit()
    flash(f'Đã xóa sinh viên {fullname} thành công', 'success')
    return redirect(url_for('students.student_list') )

@students_bp.route('/delete-multiple', methods=['POST'])
@login_required
def delete_students():
    student_ids_str = request.form.get('student_ids')
    if not student_ids_str:
        flash('Không có sinh viên nào được chọn', 'warning')
        return redirect(url_for('students.student_list'))
    student_ids = [id.strip() for id in student_ids_str.split(',') if id.strip()]
    if not student_ids:
        flash('Không có sinh viên nào được chọn', 'warning')
        return redirect(url_for('students.student_list'))
    if current_user.role not in ['admin', 'teacher']:
        flash('Bạn không có quyền xóa sinh viên', 'danger')
        return redirect(url_for('students.student_list'))
    count = 0
    for student_id in student_ids:
        student = User.query.filter_by(id=student_id, role='student').first()
        if student and can_manage_student(student):
            db.session.delete(student)
            count += 1
    if count > 0:
        db.session.commit()
        flash(f'Đã xóa {count} sinh viên thành công', 'success')
    else:
        flash('Không có sinh viên nào được xóa', 'warning')
    return redirect(url_for('students.student_list'))

@students_bp.route('/<int:id>/view')
@login_required
def view_student(id):
    student = User.query.filter_by(id=id, role='student').first_or_404()
    if not can_view_student(student):
        flash('Bạn không có quyền xem thông tin sinh viên này', 'danger')
        return redirect(url_for('students.student_list'))
    return render_template('students/view.html', student=student)

@students_bp.route('/<int:id>/certificate')
@login_required
def student_certificate(id):
    student = User.query.filter_by(id=id, role='student').first_or_404()
    if not can_view_student(student):
        flash('Bạn không có quyền xem giấy khen của sinh viên này', 'danger')
        return redirect(url_for('students.student_list'))
    if student.score is None or student.score < 8.0:
        flash('Sinh viên chưa đủ điều kiện nhận giấy khen!', 'warning')
        return redirect(url_for('students.view_student', id=student.id))
    return render_template('students/certificate.html', student=student, current_time=datetime.utcnow()) 