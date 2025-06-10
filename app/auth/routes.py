from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.auth.forms import LoginForm
from app.forms import ForgotPasswordForm, ResetPasswordForm, ChangePasswordForm
from app.models import User
from app import db, mail
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.role == form.role.data:
            login_user(user)
            flash(f'Đăng nhập thành công với vai trò {user.role}', 'success')
            if user.role == 'admin':
                return redirect(url_for('index'))
            elif user.role == 'teacher':
                return redirect(url_for('teachers.teacher_list'))
            else:
                return redirect(url_for('students.view_student', id=user.id))
        elif user and user.check_password(form.password.data) and user.role != form.role.data:
            flash(f'Vai trò không khớp. Tài khoản này có vai trò {user.role}', 'danger')
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = None
        if '@' in form.email.data:
            user = User.query.filter_by(email=form.email.data).first()
        else:
            user = User.query.filter_by(username=form.email.data).first()
        if user:
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(user.id, salt='reset-password')
            user.reset_password_token = token
            user.reset_password_expires = datetime.now() + timedelta(hours=1)
            db.session.commit()
            if user.email:
                reset_url = url_for('auth.reset_password', token=token, _external=True)
                msg = Message('Đặt lại mật khẩu', recipients=[user.email])
                msg.body = f'Để đặt lại mật khẩu, vui lòng truy cập liên kết sau: {reset_url}'
                mail.send(msg)
                flash('Hướng dẫn đặt lại mật khẩu đã được gửi đến email của bạn.', 'info')
            else:
                reset_url = url_for('auth.reset_password', token=token, _external=True)
                flash(f'Không tìm thấy email. Đây là liên kết đặt lại mật khẩu của bạn: {reset_url}', 'warning')
            return redirect(url_for('auth.login'))
        else:
            flash('Không tìm thấy tài khoản với thông tin này.', 'danger')
            return render_template('auth/forgot_password.html', form=form)
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_password_token=token).first()
    if not user or user.reset_password_expires < datetime.now():
        flash('Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.', 'danger')
        return redirect(url_for('auth.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_password_token = None
        user.reset_password_expires = None
        db.session.commit()
        flash('Mật khẩu của bạn đã được đặt lại. Bạn có thể đăng nhập ngay bây giờ.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.get_or_404(current_user.id)
        if not user.check_password(form.old_password.data):
            flash('Mật khẩu cũ không đúng.', 'danger')
        else:
            user.set_password(form.new_password.data)
            db.session.commit()
            flash('Đổi mật khẩu thành công.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('auth/change_password.html', form=form)