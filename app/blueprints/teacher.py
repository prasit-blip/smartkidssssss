"""
Teacher Blueprint for the Tutoring School Management System.

Handles teacher-specific functionality like attendance and scoring.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Teacher, Class, Enrollment, Attendance, Score, Student, Course

teacher_bp = Blueprint('teacher', __name__, template_folder='../../templates')


@teacher_bp.route('/dashboard')
@login_required
def dashboard():
    """Teacher dashboard."""
    teacher = Teacher.query.filter_by(user_id=current_user.id).first_or_404()
    classes = Class.query.filter_by(teacher_id=teacher.id).all()
    return render_template('teacher/dashboard.html', teacher=teacher, classes=classes)


@teacher_bp.route('/attendance/<int:class_id>', methods=['GET', 'POST'])
@login_required
def take_attendance(class_id):
    """Take attendance for a class."""
    class_ = Class.query.get_or_404(class_id)
    enrollments = Enrollment.query.filter_by(class_id=class_id, status='approved').all()

    if request.method == 'POST':
        attendance_date_str = request.form.get('attendance_date')
        attendance_date = datetime.strptime(attendance_date_str, '%Y-%m-%d').date() if attendance_date_str else datetime.utcnow().date()

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
        return redirect(url_for('teacher.dashboard'))

    return render_template('teacher/attendance.html', class_=class_, enrollments=enrollments)


@teacher_bp.route('/scores/<int:student_id>', methods=['GET', 'POST'])
@login_required
def enter_scores(student_id):
    """Enter scores for a student."""
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        course_id = request.form.get('course_id')
        score_value = float(request.form.get('score_value'))
        max_score = float(request.form.get('max_score', 100))
        test_name = request.form.get('test_name')
        test_date_str = request.form.get('test_date')
        test_date = datetime.strptime(test_date_str, '%Y-%m-%d').date() if test_date_str else None

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
        return redirect(url_for('teacher.dashboard'))

    courses = Course.query.all()
    return render_template('teacher/scores.html', student=student, courses=courses)
