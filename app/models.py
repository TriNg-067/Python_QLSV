from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

teacher_class = db.Table('teacher_class',
    db.Column('teacher_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('class_id', db.Integer, db.ForeignKey('class.id'), primary_key=True)
)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    students = db.relationship('User', backref='class_', lazy=True, foreign_keys='User.class_id')

from datetime import datetime

class User(db.Model, UserMixin):
    """
    Các role hợp lệ:
    - admin: Quản trị viên toàn hệ thống
    - teacher: Giảng viên/Chuyên viên
    - student: Sinh viên
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True)
    fullname = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    birthdate = db.Column(db.Date)
    gender = db.Column(db.String(10))
    avatar = db.Column(db.String(255))
    teacher_code = db.Column(db.String(20), unique=True)
    student_code = db.Column(db.String(20), unique=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    score = db.Column(db.Float)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reset_password_token = db.Column(db.String(128))
    reset_password_expires = db.Column(db.DateTime)
    classes = db.relationship('Class', secondary=teacher_class, backref='teachers')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_assigned_classes(self):
        # Trả về danh sách lớp mà giáo viên phụ trách (từ quan hệ N-N)
        return self.classes or []

    def can_manage_class(self, class_name):
        if self.role == 'admin':
            return True
        if self.role != 'teacher':
            return False
        return any(c.name == class_name for c in self.classes)

    def average_score(self):
        # Tính điểm trung bình của tất cả sinh viên thuộc các lớp mà giáo viên phụ trách
        students = []
        for c in self.classes:
            students.extend(c.students)
        scores = [s.score for s in students if hasattr(s, 'score') and s.score is not None]
        if not scores:
            return None
        return round(sum(scores) / len(scores), 2)