from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
csrf = CSRFProtect(app)

from app import models
from app.auth.routes import auth_bp
from app.students import students_bp
from app.reports import reports_bp
from app.teachers import teachers_bp
from app.classes import classes_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(students_bp, url_prefix='/students')
app.register_blueprint(reports_bp, url_prefix='/reports')
app.register_blueprint(teachers_bp, url_prefix='/teachers')
app.register_blueprint(classes_bp, url_prefix='/classes')

@app.route('/')
@login_required
def index():
    from flask import render_template
    from flask_login import current_user
    from app.models import User, Class
    from sqlalchemy import func
    # Tổng số sinh viên
    total_students = User.query.filter_by(role='student').count()
    # Sinh viên đạt giỏi (giả sử điểm >= 8 là giỏi)
    excellent_students = User.query.filter_by(role='student').filter(User.score >= 8).count()
    # Tổng số lớp học
    total_classes = Class.query.count()
    # Tổng số giảng viên
    total_teachers = User.query.filter_by(role='teacher').count()
    # Số lớp đã phân công giảng viên (có ít nhất 1 teacher)
    assigned_classes = Class.query.join(Class.teachers).distinct().count()
    # Tỷ lệ SV/GV (nếu total_teachers > 0)
    sv_gv_ratio = round(total_students / total_teachers, 1) if total_teachers else 0
    # Lấy 5 sinh viên mới nhất theo id (nếu không có created_at/updated_at)
    latest_students = User.query.filter_by(role='student').order_by(User.updated_at.desc()).limit(5).all()
    # Thống kê điểm số
    score_ranges = {
        'Dưới 5': 0,
        '5-6.4': 0,
        '6.5-7.9': 0,
        '8-8.9': 0,
        '9-10': 0
    }
    gender_stats = {'Nam': 0, 'Nữ': 0, 'Khác': 0}
    students = User.query.filter_by(role='student').all()
    for s in students:
        if s.score is not None:
            if s.score < 5:
                score_ranges['Dưới 5'] += 1
            elif s.score < 6.5:
                score_ranges['5-6.4'] += 1
            elif s.score < 8:
                score_ranges['6.5-7.9'] += 1
            elif s.score < 9:
                score_ranges['8-8.9'] += 1
            else:
                score_ranges['9-10'] += 1
        if s.gender == 'Nam':
            gender_stats['Nam'] += 1
        elif s.gender == 'Nữ':
            gender_stats['Nữ'] += 1
        else:
            gender_stats['Khác'] += 1
    return render_template(
        'index.html',
        total_students=total_students,
        excellent_students=excellent_students,
        total_classes=total_classes,
        assigned_classes=assigned_classes,
        total_teachers=total_teachers,
        sv_gv_ratio=sv_gv_ratio,
        latest_students=latest_students,
        score_ranges=score_ranges,
        gender_stats=gender_stats
    )

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))