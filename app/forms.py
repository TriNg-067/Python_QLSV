from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField, FloatField, PasswordField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional, ValidationError
from app.models import User, Class
import re

def strong_password(form, field):
    password = field.data or ''
    if len(password) < 8:
        raise ValidationError('Mật khẩu phải có ít nhất 8 ký tự.')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Mật khẩu phải chứa ít nhất 1 chữ hoa.')
    if not re.search(r'[0-9]', password):
        raise ValidationError('Mật khẩu phải chứa ít nhất 1 số.')
    if not re.search(r'[^A-Za-z0-9]', password):
        raise ValidationError('Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt.')

class StudentForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Mật khẩu', validators=[Optional(), strong_password])
    student_code = StringField('Mã SV', validators=[DataRequired(), Length(min=2, max=20)])
    fullname = StringField('Họ và tên', validators=[DataRequired(), Length(max=100)])
    birthdate = DateField('Ngày sinh', validators=[Optional()])
    gender = SelectField('Giới tính', choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')], validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    class_id = SelectField('Lớp', coerce=int, validators=[DataRequired()])
    score = FloatField('Điểm', validators=[Optional(), NumberRange(min=0, max=10, message='Điểm phải từ 0 đến 10')])
    avatar = StringField('Ảnh đại diện (URL)', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Lưu')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_id.choices = [(c.id, c.name) for c in Class.query.order_by(Class.name).all()]

    def validate_student_code(self, student_code):
        student = User.query.filter_by(student_code=student_code.data).first()
        if student and (not hasattr(self, 'student_id') or student.id != self.student_id):
            raise ValidationError('Mã sinh viên này đã tồn tại. Vui lòng sử dụng mã khác.')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email hoặc tên đăng nhập', validators=[DataRequired()])
    submit = SubmitField('Gửi yêu cầu')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Mật khẩu mới', validators=[
        DataRequired(),
        strong_password
    ])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[
        DataRequired(),
        EqualTo('password', message='Mật khẩu xác nhận không khớp')
    ])
    submit = SubmitField('Đặt lại mật khẩu')

class TeacherProfileForm(FlaskForm):
    avatar = StringField('Ảnh đại diện (URL)', validators=[Optional(), Length(max=255)])
    fullname = StringField('Họ và tên', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Số điện thoại', validators=[Optional(), Length(max=20)])
    birthdate = DateField('Ngày sinh', format='%Y-%m-%d', validators=[Optional()])
    gender = SelectField('Giới tính', choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')], validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    submit = SubmitField('Lưu thông tin')

class TeacherCreateForm(FlaskForm):
    teacher_code = StringField('Mã GV', validators=[DataRequired(), Length(min=2, max=20)])
    fullname = StringField('Họ và tên', validators=[DataRequired(), Length(max=100)])
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Mật khẩu', validators=[DataRequired(), strong_password])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('password', message='Mật khẩu xác nhận không khớp')])
    birthdate = DateField('Ngày sinh', format='%Y-%m-%d', validators=[Optional()])
    gender = SelectField('Giới tính', choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')], validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    phone = StringField('Số điện thoại', validators=[Optional(), Length(max=20)])
    avatar = StringField('Ảnh đại diện (URL)', validators=[Optional(), Length(max=255)])
    classes = SelectMultipleField('Các lớp phụ trách', coerce=int, validators=[Optional()])
    submit = SubmitField('Thêm giảng viên')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes.choices = [(c.id, c.name) for c in Class.query.order_by(Class.name).all()]

    def validate_teacher_code(self, teacher_code):
        from app.models import User
        user = User.query.filter_by(teacher_code=teacher_code.data).first()
        if user:
            raise ValidationError('Mã giảng viên đã tồn tại.')

    def validate_username(self, username):
        from app.models import User
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Tên đăng nhập đã tồn tại.')

    def validate_email(self, email):
        from app.models import User
        if email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email đã tồn tại.')

class TeacherForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Mật khẩu', validators=[Optional(), strong_password])
    teacher_code = StringField('Mã GV', validators=[DataRequired(), Length(min=2, max=20)])
    fullname = StringField('Họ và tên', validators=[DataRequired(), Length(max=100)])
    birthdate = DateField('Ngày sinh', validators=[Optional()])
    gender = SelectField('Giới tính', choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')], validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    phone = StringField('SĐT', validators=[Optional(), Length(max=20)])
    avatar = StringField('Ảnh đại diện (URL)', validators=[Optional(), Length(max=255)])
    classes = SelectMultipleField('Các lớp phụ trách', coerce=int, validators=[Optional()])
    submit = SubmitField('Lưu')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes.choices = [(c.id, c.name) for c in Class.query.order_by(Class.name).all()]

class ClassForm(FlaskForm):
    name = StringField('Tên lớp', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Lưu')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Mật khẩu cũ', validators=[DataRequired()])
    new_password = PasswordField('Mật khẩu mới', validators=[DataRequired(), strong_password])
    confirm_new_password = PasswordField('Xác nhận mật khẩu mới', validators=[DataRequired(), EqualTo('new_password', message='Mật khẩu xác nhận không khớp')])
    submit = SubmitField('Đổi mật khẩu')