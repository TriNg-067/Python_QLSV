from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired

# Form đăng nhập với username, password và role
class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    role = RadioField('Vai trò', choices=[
        ('admin', 'Quản trị viên'),
        ('teacher', 'Giảng viên'),
        ('student', 'Sinh viên')
    ], default='student', validators=[DataRequired()])
    submit = SubmitField('Đăng nhập')