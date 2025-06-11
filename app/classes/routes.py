from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Class
from app.classes import classes_bp
from app.rules.permissions import admin_required
from app.forms import ClassForm
from app import db

@classes_bp.route('/')
@classes_bp.route('/list')
@login_required
def class_list():
    classes = Class.query.order_by(Class.name).all()
    return render_template('classes/index.html', classes=classes)

@classes_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_class():
    form = ClassForm()
    if form.validate_on_submit():
        # Kiểm tra xem lớp đã tồn tại chưa
        existing_class = Class.query.filter_by(name=form.name.data).first()
        if existing_class:
            flash('Mã lớp đã tồn tại! Vui lòng nhập mã lớp khác.', 'danger')
            return render_template('classes/create_edit.html', form=form, action='create')
        new_class = Class(name=form.name.data)
        db.session.add(new_class)
        db.session.commit()
        flash('Đã thêm lớp học mới!', 'success')
        return redirect(url_for('classes.class_list'))
    return render_template('classes/create_edit.html', form=form, action='create')

@classes_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_class(id):
    class_obj = Class.query.get_or_404(id)
    form = ClassForm(obj=class_obj)
    if form.validate_on_submit():
           # Kiểm tra xem lớp đã tồn tại chưa, loại trừ lớp hiện tại
        existing_class = Class.query.filter(Class.name == form.name.data, Class.id != id).first()
        if existing_class:
            flash('Mã lớp đã tồn tại! Vui lòng nhập mã lớp khác.', 'danger')
            return render_template('classes/create_edit.html', form=form, action='edit')
        class_obj.name = form.name.data
        db.session.commit()
        flash('Đã cập nhật tên lớp!', 'success')
        return redirect(url_for('classes.class_list'))
    return render_template('classes/create_edit.html', form=form, action='edit')

@classes_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_class(id):
    class_obj = Class.query.get_or_404(id)
    db.session.delete(class_obj)
    db.session.commit()
    flash('Đã xoá lớp học!', 'success')
    return redirect(url_for('classes.class_list')) 