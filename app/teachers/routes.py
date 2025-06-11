from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, Class, db
from app.teachers import teachers_bp
from app.forms import TeacherProfileForm, TeacherCreateForm, TeacherForm
from app.rules.permissions import admin_required, teacher_required
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email, ValidationError

@teachers_bp.route('/')
@teachers_bp.route('/list')
@login_required
def teacher_list():
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'teacher_code')
    sort_order = request.args.get('sort_order', 'asc')
    page = int(request.args.get('page', 1))
    per_page = 15
    if current_user.role == 'admin':
        query = User.query.filter_by(role='teacher')
        if search:
            query = query.filter((User.teacher_code.ilike(f'%{search}%')) | (User.fullname.ilike(f'%{search}%')))
        # Sắp xếp
        if sort_by == 'teacher_code':
            if sort_order == 'asc':
                query = query.order_by(User.teacher_code.asc())
            else:
                query = query.order_by(User.teacher_code.desc())
        elif sort_by == 'fullname':
            if sort_order == 'asc':
                query = query.order_by(User.fullname.asc())
            else:
                query = query.order_by(User.fullname.desc())
        else:
            query = query.order_by(User.teacher_code.asc())
        total = query.count()
        total_pages = (total + per_page - 1) // per_page
        teachers_page = query.offset((page-1)*per_page).limit(per_page).all()
        total_classes = Class.query.count()
        all_students = User.query.filter_by(role='student').filter(User.score != None).all()
        avg_score = round(sum([s.score for s in all_students]) / len(all_students), 2) if all_students else None
        return render_template('teachers/index.html', teachers=teachers_page, is_admin=True, search=search, sort_by=sort_by, sort_order=sort_order, total_classes=total_classes, avg_score=avg_score, page=page, total_pages=total_pages)
    elif current_user.role == 'teacher':
        return render_template('teachers/index.html', teachers=[current_user], is_admin=False, search=search, sort_by=sort_by, sort_order=sort_order, page=1, total_pages=1)
    else:
        return render_template('teachers/index.html', teachers=[], is_admin=False, search=search, sort_by=sort_by, sort_order=sort_order, page=1, total_pages=1)

@teachers_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_profile():
    form = TeacherProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.avatar = form.avatar.data
        current_user.fullname = form.fullname.data
        current_user.phone = form.phone.data
        current_user.birthdate = form.birthdate.data
        current_user.gender = form.gender.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Cập nhật thông tin thành công!', 'success')
        return redirect(url_for('teachers.teacher_list'))
    return render_template('teachers/edit_profile.html', form=form)

@teachers_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_teacher():
    form = TeacherCreateForm()
    if form.validate_on_submit():
        user = User(
            teacher_code=form.teacher_code.data,
            fullname=form.fullname.data,
            username=form.username.data,
            email=form.email.data,
            phone=form.phone.data,
            birthdate=form.birthdate.data,
            gender=form.gender.data,
            avatar=form.avatar.data,
            role='teacher'
        )
        user.set_password(form.password.data)
        # Gán các lớp phụ trách
        user.classes = Class.query.filter(Class.id.in_(form.classes.data)).all()
        db.session.add(user)
        db.session.commit()
        flash('Thêm giảng viên thành công!', 'success')
        return redirect(url_for('teachers.teacher_list'))
    return render_template('teachers/create_teacher.html', form=form)

@teachers_bp.route('/delete', methods=['POST'])
@login_required
@admin_required
def delete_teachers():
    ids = request.form.get('teacher_ids', '')
    if not ids:
        flash('Không có giảng viên nào được chọn để xoá.', 'warning')
        return redirect(url_for('teachers.teacher_list'))
    id_list = [int(i) for i in ids.split(',') if i.isdigit()]
    deleted = 0
    for uid in id_list:
        user = User.query.filter_by(id=uid, role='teacher').first()
        if user:
            db.session.delete(user)
            deleted += 1
    db.session.commit()
    flash(f'Đã xoá {deleted} giảng viên.', 'success')
    return redirect(url_for('teachers.teacher_list'))

@teachers_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_teacher(id):
    user = User.query.filter_by(id=id, role='teacher').first_or_404()
    form = TeacherForm(obj=user)
    if request.method == 'GET':
        form.classes.data = [c.id for c in user.classes]
    if form.validate_on_submit():
        user.teacher_code = form.teacher_code.data
        user.fullname = form.fullname.data
        user.username = form.username.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.birthdate = form.birthdate.data
        user.gender = form.gender.data
        user.avatar = form.avatar.data
        # Gán lại các lớp phụ trách
        user.classes = Class.query.filter(Class.id.in_(form.classes.data)).all()
        db.session.commit()
        flash('Cập nhật thông tin giảng viên thành công!', 'success')
        return redirect(url_for('teachers.teacher_list'))
    return render_template('teachers/edit_teacher.html', form=form, teacher=user) 