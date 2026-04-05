"""
Database models for the Tutoring School Management System.

This module defines all SQLAlchemy models used in the application.
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    """User model for authentication and authorization."""
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)  # admin, parent, teacher
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_profile = db.relationship('Parent', backref='user', uselist=False, cascade='all, delete-orphan')
    teacher_profile = db.relationship('Teacher', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the user's password."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class Parent(db.Model):
    """Parent/Guardian model."""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    line_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', backref='parent', lazy='dynamic', cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='parent', lazy='dynamic')
    payments = db.relationship('Payment', backref='parent', lazy='dynamic')
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Parent {self.full_name}>'


class Teacher(db.Model):
    """Teacher model."""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    specialization = db.Column(db.String(100))  # Math, English, Science
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    classes = db.relationship('Class', backref='teacher', lazy='dynamic')
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Teacher {self.full_name}>'


class Student(db.Model):
    """Student model."""
    
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    school = db.Column(db.String(200))
    grade_level = db.Column(db.String(20), nullable=False, index=True)  # ป.1 - ป.6
    date_of_birth = db.Column(db.Date)
    profile_image = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic')
    attendance_records = db.relationship('Attendance', backref='student', lazy='dynamic')
    scores = db.relationship('Score', backref='student', lazy='dynamic')
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Student {self.full_name}>'


class Branch(db.Model):
    """Branch/School location model."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    opening_hours = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    courses = db.relationship('Course', backref='branch', lazy='dynamic')
    classes = db.relationship('Class', backref='branch', lazy='dynamic')
    
    def __repr__(self):
        return f'<Branch {self.name}>'


class Course(db.Model):
    """Course model."""
    
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False, index=True)
    subject = db.Column(db.String(50), nullable=False, index=True)  # Math, English, Science
    name = db.Column(db.String(200), nullable=False)
    grade_level = db.Column(db.String(20), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    total_hours = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    classes = db.relationship('Class', backref='course', lazy='dynamic')
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic')
    
    def __repr__(self):
        return f'<Course {self.name}>'


class Class(db.Model):
    """Class schedule model."""
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False, index=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False, index=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False, index=True)
    day_of_week = db.Column(db.String(20), nullable=False)  # Monday, Tuesday, etc.
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    room_number = db.Column(db.String(50))
    max_students = db.Column(db.Integer, default=20)
    is_recurring = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='class_', lazy='dynamic')
    attendance_records = db.relationship('Attendance', backref='class_', lazy='dynamic')
    
    def __repr__(self):
        return f'<Class {self.course_id} - {self.day_of_week}>'


class Enrollment(db.Model):
    """Enrollment model for student course registrations."""
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False, index=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False, index=True)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, approved, cancelled
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='enrollment', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Enrollment {self.student_id} - {self.course_id}>'


class Payment(db.Model):
    """Payment model for course fees."""
    
    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollment.id'), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))  # bank_transfer, qrcode, online
    status = db.Column(db.String(20), default='pending', index=True)  # pending, approved, rejected
    slip_filename = db.Column(db.String(256))
    transfer_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    approver = db.relationship('User', foreign_keys=[approved_by])
    
    def __repr__(self):
        return f'<Payment {self.id} - {self.status}>'


class Attendance(db.Model):
    """Attendance tracking model."""
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, index=True)
    attendance_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False)  # present, absent, late, leave
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)
    checked_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Attendance {self.student_id} - {self.attendance_date}>'


class Score(db.Model):
    """Student score/grade model."""
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False, index=True)
    score_value = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, default=100)
    test_name = db.Column(db.String(200))
    test_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<Score {self.student_id} - {self.test_name}>'


class News(db.Model):
    """News/Announcement model."""
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    published_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    def __repr__(self):
        return f'<News {self.title}>'
