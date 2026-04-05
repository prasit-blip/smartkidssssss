from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tutoring_school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'กรุณาเข้าสู่ระบบเพื่อใช้งานหน้านี้'

# ==================== DATABASE MODELS ====================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, parent, teacher
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    parent_profile = db.relationship('Parent', backref='user', uselist=False)
    teacher_profile = db.relationship('Teacher', backref='user', uselist=False)

class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    line_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', backref='parent', lazy=True)
    enrollments = db.relationship('Enrollment', backref='parent', lazy=True)
    payments = db.relationship('Payment', backref='parent', lazy=True)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    specialization = db.Column(db.String(100))  # Math, English, Science
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    classes = db.relationship('Class', backref='teacher', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    school = db.Column(db.String(200))
    grade_level = db.Column(db.String(20), nullable=False)  # ป.1 - ป.6
    date_of_birth = db.Column(db.Date)
    profile_image = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)
    scores = db.relationship('Score', backref='student', lazy=True)

class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    opening_hours = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    courses = db.relationship('Course', backref='branch', lazy=True)
    classes = db.relationship('Class', backref='branch', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)  # Math, English, Science
    name = db.Column(db.String(200), nullable=False)
    grade_level = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_hours = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    classes = db.relationship('Class', backref='course', lazy=True)
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
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
    enrollments = db.relationship('Enrollment', backref='class_', lazy=True)
    attendance_records = db.relationship('Attendance', backref='class_', lazy=True)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, cancelled
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='enrollment', lazy=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollment.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))  # bank_transfer, qrcode, online
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    slip_filename = db.Column(db.String(256))
    transfer_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    approver = db.relationship('User', foreign_keys=[approved_by])

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # present, absent, late, leave
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)
    checked_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    notes = db.Column(db.Text)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    score_value = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, default=100)
    test_name = db.Column(db.String(200))
    test_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== DECORATORS ====================

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role not in roles:
                flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== ROUTES ====================

@app.route('/')
def index():
    news = News.query.filter_by(is_active=True).order_by(News.published_at.desc()).limit(5).all()
    branches = Branch.query.filter_by(is_active=True).all()
    return render_template('index.html', news=news, branches=branches)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        
        if password != confirm_password:
            flash('รหัสผ่านไม่ตรงกัน', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('อีเมลนี้ถูกใช้งานแล้ว', 'error')
            return render_template('register.html')
        
        user = User(email=email, password_hash=generate_password_hash(password), role='parent')
        db.session.add(user)
        db.session.commit()
        
        parent = Parent(
            user_id=user.id,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        db.session.add(parent)
        db.session.commit()
        
        flash('สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=bool(remember))
            next_page = request.args.get('next')
            
            if user.role == 'admin':
                return redirect(next_page or url_for('admin_dashboard'))
            elif user.role == 'teacher':
                return redirect(next_page or url_for('teacher_dashboard'))
            else:
                return redirect(next_page or url_for('parent_dashboard'))
        else:
            flash('อีเมลหรือรหัสผ่านไม่ถูกต้อง', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ออกจากระบบเรียบร้อยแล้ว', 'success')
    return redirect(url_for('index'))

# ==================== PARENT ROUTES ====================

@app.route('/parent/dashboard')
@login_required
@role_required('parent')
def parent_dashboard():
    parent = Parent.query.filter_by(user_id=current_user.id).first()
    students = Student.query.filter_by(parent_id=parent.id).all()
    enrollments = Enrollment.query.filter_by(parent_id=parent.id).order_by(Enrollment.enrolled_at.desc()).all()
    payments = Payment.query.filter_by(parent_id=parent.id).order_by(Payment.created_at.desc()).all()
    
    return render_template('parent/dashboard.html', 
                         parent=parent, 
                         students=students, 
                         enrollments=enrollments,
                         payments=payments)

@app.route('/parent/add-student', methods=['GET', 'POST'])
@login_required
@role_required('parent')
def add_student():
    if request.method == 'POST':
        parent = Parent.query.filter_by(user_id=current_user.id).first()
        
        student = Student(
            parent_id=parent.id,
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            school=request.form.get('school'),
            grade_level=request.form.get('grade_level'),
            date_of_birth=datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date() if request.form.get('date_of_birth') else None
        )
        db.session.add(student)
        db.session.commit()
        
        flash('เพิ่มนักเรียนสำเร็จ', 'success')
        return redirect(url_for('parent_dashboard'))
    
    return render_template('parent/add_student.html')

@app.route('/courses')
@login_required
def courses():
    branch_id = request.args.get('branch_id', type=int)
    grade_level = request.args.get('grade_level')
    subject = request.args.get('subject')
    
    query = Course.query.filter_by(is_active=True)
    
    if branch_id:
        query = query.filter_by(branch_id=branch_id)
    if grade_level:
        query = query.filter_by(grade_level=grade_level)
    if subject:
        query = query.filter_by(subject=subject)
    
    courses = query.all()
    branches = Branch.query.filter_by(is_active=True).all()
    
    return render_template('courses.html', courses=courses, branches=branches)

@app.route('/enroll/<int:course_id>', methods=['GET', 'POST'])
@login_required
@role_required('parent')
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    parent = Parent.query.filter_by(user_id=current_user.id).first()
    classes = Class.query.filter_by(course_id=course_id).all()
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        class_id = request.form.get('class_id')
        
        if not student_id or not class_id:
            flash('กรุณาเลือกนักเรียนและตารางเรียน', 'error')
            return render_template('enroll.html', course=course, classes=classes, parent=parent)
        
        enrollment = Enrollment(
            student_id=student_id,
            parent_id=parent.id,
            course_id=course_id,
            class_id=class_id,
            status='pending'
        )
        db.session.add(enrollment)
        db.session.commit()
        
        flash('ลงทะเบียนเรียนสำเร็จ! รอการอนุมัติและชำระเงิน', 'success')
        return redirect(url_for('make_payment', enrollment_id=enrollment.id))
    
    students = Student.query.filter_by(parent_id=parent.id).all()
    return render_template('enroll.html', course=course, classes=classes, students=students, parent=parent)

@app.route('/payment/<int:enrollment_id>', methods=['GET', 'POST'])
@login_required
@role_required('parent')
def make_payment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        payment_method = request.form.get('payment_method')
        transfer_date = datetime.strptime(request.form.get('transfer_date'), '%Y-%m-%dT%H:%M')
        
        slip_file = request.files.get('slip')
        slip_filename = None
        
        if slip_file and slip_file.filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            slip_filename = f"slip_{timestamp}_{slip_file.filename}"
            slip_file.save(os.path.join(app.config['UPLOAD_FOLDER'], slip_filename))
        
        payment = Payment(
            enrollment_id=enrollment_id,
            parent_id=enrollment.parent_id,
            amount=amount,
            payment_method=payment_method,
            status='pending',
            slip_filename=slip_filename,
            transfer_date=transfer_date,
            notes=request.form.get('notes')
        )
        db.session.add(payment)
        db.session.commit()
        
        flash('อัปโหลดสลิปการโอนเงินสำเร็จ! รอการตรวจสอบ', 'success')
        return redirect(url_for('parent_dashboard'))
    
    return render_template('payment.html', enrollment=enrollment)

# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    total_students = Student.query.count()
    total_parents = Parent.query.count()
    total_teachers = Teacher.query.count()
    total_courses = Course.query.count()
    
    recent_enrollments = Enrollment.query.order_by(Enrollment.enrolled_at.desc()).limit(10).all()
    pending_payments = Payment.query.filter_by(status='pending').all()
    
    # Revenue calculation (approved payments only)
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter_by(status='approved').scalar() or 0
    
    return render_template('admin/dashboard.html',
                         total_students=total_students,
                         total_parents=total_parents,
                         total_teachers=total_teachers,
                         total_courses=total_courses,
                         recent_enrollments=recent_enrollments,
                         pending_payments=pending_payments,
                         total_revenue=total_revenue)

@app.route('/admin/payments')
@login_required
@role_required('admin')
def admin_payments():
    status_filter = request.args.get('status', 'pending')
    payments = Payment.query.filter_by(status=status_filter).order_by(Payment.created_at.desc()).all()
    return render_template('admin/payments.html', payments=payments, status_filter=status_filter)

@app.route('/admin/approve-payment/<int:payment_id>', methods=['POST'])
@login_required
@role_required('admin')
def approve_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    action = request.form.get('action')
    
    if action == 'approve':
        payment.status = 'approved'
        payment.approved_by = current_user.id
        payment.approved_at = datetime.utcnow()
        payment.enrollment.status = 'approved'
        flash('อนุมัติการชำระเงินสำเร็จ', 'success')
    elif action == 'reject':
        payment.status = 'rejected'
        payment.approved_by = current_user.id
        payment.approved_at = datetime.utcnow()
        flash('ปฏิเสธการชำระเงิน', 'error')
    
    db.session.commit()
    return redirect(url_for('admin_payments'))

@app.route('/admin/students')
@login_required
@role_required('admin')
def admin_students():
    students = Student.query.order_by(Student.created_at.desc()).all()
    return render_template('admin/students.html', students=students)

@app.route('/admin/teachers')
@login_required
@role_required('admin')
def admin_teachers():
    teachers = Teacher.query.all()
    return render_template('admin/teachers.html', teachers=teachers)

@app.route('/admin/courses')
@login_required
@role_required('admin')
def admin_courses():
    courses = Course.query.all()
    branches = Branch.query.all()
    return render_template('admin/courses.html', courses=courses, branches=branches)

@app.route('/admin/branches')
@login_required
@role_required('admin')
def admin_branches():
    branches = Branch.query.all()
    return render_template('admin/branches.html', branches=branches)

# ==================== TEACHER ROUTES ====================

@app.route('/teacher/dashboard')
@login_required
@role_required('teacher')
def teacher_dashboard():
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    classes = Class.query.filter_by(teacher_id=teacher.id).all()
    return render_template('teacher/dashboard.html', teacher=teacher, classes=classes)

@app.route('/teacher/attendance/<int:class_id>', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
def take_attendance(class_id):
    class_ = Class.query.get_or_404(class_id)
    enrollments = Enrollment.query.filter_by(class_id=class_id, status='approved').all()
    
    if request.method == 'POST':
        attendance_date = datetime.strptime(request.form.get('attendance_date'), '%Y-%m-%d').date()
        
        for enrollment in enrollments:
            status = request.form.get(f'status_{enrollment.student_id}')
            notes = request.form.get(f'notes_{enrollment.student_id}', '')
            
            if status:
                attendance = Attendance(
                    class_id=class_id,
                    student_id=enrollment.student_id,
                    attendance_date=attendance_date,
                    status=status,
                    checked_by=current_user.id,
                    notes=notes
                )
                db.session.add(attendance)
        
        db.session.commit()
        flash('บันทึกการเข้าเรียนสำเร็จ', 'success')
        return redirect(url_for('teacher_dashboard'))
    
    return render_template('teacher/attendance.html', class_=class_, enrollments=enrollments)

@app.route('/teacher/scores/<int:student_id>', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
def enter_scores(student_id):
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'POST':
        course_id = request.form.get('course_id')
        score_value = float(request.form.get('score_value'))
        max_score = float(request.form.get('max_score', 100))
        test_name = request.form.get('test_name')
        test_date = datetime.strptime(request.form.get('test_date'), '%Y-%m-%d').date() if request.form.get('test_date') else None
        
        score = Score(
            student_id=student_id,
            course_id=course_id,
            score_value=score_value,
            max_score=max_score,
            test_name=test_name,
            test_date=test_date,
            created_by=current_user.id
        )
        db.session.add(score)
        db.session.commit()
        
        flash('บันทึกคะแนนสำเร็จ', 'success')
        return redirect(url_for('teacher_dashboard'))
    
    courses = Course.query.all()
    return render_template('teacher/scores.html', student=student, courses=courses)

# ==================== API ENDPOINTS ====================

@app.route('/api/students')
@login_required
def api_get_students():
    parent = Parent.query.filter_by(user_id=current_user.id).first()
    students = Student.query.filter_by(parent_id=parent.id).all()
    
    return jsonify([{
        'id': s.id,
        'first_name': s.first_name,
        'last_name': s.last_name,
        'grade_level': s.grade_level,
        'school': s.school
    } for s in students])

@app.route('/api/enroll', methods=['POST'])
@login_required
@role_required('parent')
def api_enroll():
    data = request.get_json()
    parent = Parent.query.filter_by(user_id=current_user.id).first()
    
    enrollment = Enrollment(
        student_id=data['student_id'],
        parent_id=parent.id,
        course_id=data['course_id'],
        class_id=data['class_id'],
        status='pending'
    )
    db.session.add(enrollment)
    db.session.commit()
    
    return jsonify({'message': 'Enrollment created successfully', 'enrollment_id': enrollment.id}), 201

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# ==================== INITIALIZE DB ====================

def create_sample_data():
    # Create admin user
    admin = User(email='admin@school.com', password_hash=generate_password_hash('admin123'), role='admin')
    db.session.add(admin)
    
    # Create sample branch
    branch = Branch(name='สาขาหลัก - สีลม', address='123 ถนนสีลม กรุงเทพฯ', phone='02-123-4567', opening_hours='09:00-20:00')
    db.session.add(branch)
    
    # Create sample courses
    courses = [
        Course(branch_id=1, subject='Math', name='คณิตศาสตร์พื้นฐาน ป.1', grade_level='ป.1', price=3000, total_hours=20, description='เรียนคณิตศาสตร์พื้นฐาน'),
        Course(branch_id=1, subject='English', name='ภาษาอังกฤษ ป.2', grade_level='ป.2', price=3500, total_hours=20, description='เรียนภาษาอังกฤษพื้นฐาน'),
        Course(branch_id=1, subject='Science', name='วิทยาศาสตร์ ป.3', grade_level='ป.3', price=3500, total_hours=20, description='เรียนวิทยาศาสตร์พื้นฐาน'),
    ]
    for course in courses:
        db.session.add(course)
    
    db.session.commit()
    print("Sample data created!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Uncomment the line below to create sample data on first run
        # if not User.query.first():
        #     create_sample_data()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
