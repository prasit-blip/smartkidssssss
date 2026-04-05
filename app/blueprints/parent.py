"""
Parent Blueprint for the Tutoring School Management System.

Handles parent-specific functionality like student management, enrollment, and payments.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import Parent, Student, Course, Class, Enrollment, Payment

parent_bp = Blueprint('parent', __name__, template_folder='../../templates')


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@parent_bp.route('/dashboard')
@login_required
def dashboard():
    """Parent dashboard."""
    parent = Parent.query.filter_by(user_id=current_user.id).first_or_404()
    students = Student.query.filter_by(parent_id=parent.id).all()
    enrollments = Enrollment.query.filter_by(parent_id=parent.id)\
        .order_by(Enrollment.enrolled_at.desc()).all()
    payments = Payment.query.filter_by(parent_id=parent.id)\
        .order_by(Payment.created_at.desc()).all()
    
    return render_template('parent/dashboard.html',
                         parent=parent,
                         students=students,
                         enrollments=enrollments,
                         payments=payments)


@parent_bp.route('/add-student', methods=['GET', 'POST'])
@login_required
def add_student():
    """Add a new student."""
    if request.method == 'POST':
        parent = Parent.query.filter_by(user_id=current_user.id).first_or_404()
        
        student = Student(
            parent_id=parent.id,
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            school=request.form.get('school'),
            grade_level=request.form.get('grade_level'),
            date_of_birth=datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date() 
                if request.form.get('date_of_birth') else None
        )
        
        # Handle profile image upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{datetime.utcnow().timestamp()}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                student.profile_image = filename
        
        db.session.add(student)
        db.session.commit()
        
        flash('เพิ่มนักเรียนสำเร็จ', 'success')
        return redirect(url_for('parent.dashboard'))
    
    return render_template('parent/add_student.html')


@parent_bp.route('/enroll/<int:course_id>', methods=['GET', 'POST'])
@login_required
def enroll(course_id):
    """Enroll a student in a course."""
    course = Course.query.get_or_404(course_id)
    parent = Parent.query.filter_by(user_id=current_user.id).first_or_404()
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
        return redirect(url_for('parent.make_payment', enrollment_id=enrollment.id))
    
    students = Student.query.filter_by(parent_id=parent.id).all()
    return render_template('enroll.html', course=course, classes=classes, students=students, parent=parent)


@parent_bp.route('/payment/<int:enrollment_id>', methods=['GET', 'POST'])
@login_required
def make_payment(enrollment_id):
    """Make payment for an enrollment."""
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        payment_method = request.form.get('payment_method')
        transfer_date_str = request.form.get('transfer_date')
        notes = request.form.get('notes')
        
        transfer_date = None
        if transfer_date_str:
            transfer_date = datetime.strptime(transfer_date_str, '%Y-%m-%d')
        
        # Handle slip upload
        slip_filename = None
        if 'slip' in request.files:
            file = request.files['slip']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"slip_{datetime.utcnow().timestamp()}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                slip_filename = filename
        
        payment = Payment(
            enrollment_id=enrollment.id,
            parent_id=enrollment.parent_id,
            amount=amount,
            payment_method=payment_method,
            slip_filename=slip_filename,
            transfer_date=transfer_date,
            notes=notes,
            status='pending'
        )
        db.session.add(payment)
        db.session.commit()
        
        flash('อัปโหลดสลิปการโอนเงินสำเร็จ! รอการตรวจสอบจากเจ้าหน้าที่', 'success')
        return redirect(url_for('parent.dashboard'))
    
    return render_template('payment.html', enrollment=enrollment)
