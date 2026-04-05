"""
Admin Blueprint for the Tutoring School Management System.

Handles admin-specific functionality like user management, payment approval, and reports.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import User, Parent, Teacher, Student, Branch, Course, Class, Enrollment, Payment, News

admin_bp = Blueprint('admin', __name__, template_folder='../../templates')


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard with statistics."""
    # Get statistics
    total_students = Student.query.count()
    total_parents = Parent.query.count()
    total_teachers = Teacher.query.count()
    total_courses = Course.query.filter_by(is_active=True).count()
    
    # Recent payments
    recent_payments = Payment.query.order_by(Payment.created_at.desc()).limit(10).all()
    
    # Revenue this month
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    revenue_this_month = db.session.query(db.func.sum(Payment.amount))\
        .filter(Payment.status == 'approved')\
        .filter(Payment.approved_at >= month_start)\
        .scalar() or 0
    
    return render_template('admin/dashboard.html',
                         total_students=total_students,
                         total_parents=total_parents,
                         total_teachers=total_teachers,
                         total_courses=total_courses,
                         recent_payments=recent_payments,
                         revenue_this_month=revenue_this_month)


@admin_bp.route('/payments')
@login_required
def payments():
    """View all payments."""
    status_filter = request.args.get('status', 'pending')
    query = Payment.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    payments = query.order_by(Payment.created_at.desc()).all()
    return render_template('admin/payments.html', payments=payments, status_filter=status_filter)


@admin_bp.route('/payments/<int:payment_id>/approve', methods=['POST'])
@login_required
def approve_payment(payment_id):
    """Approve or reject a payment."""
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
    return redirect(url_for('admin.payments'))


@admin_bp.route('/students')
@login_required
def students():
    """View all students."""
    students = Student.query.order_by(Student.created_at.desc()).all()
    return render_template('admin/students.html', students=students)


@admin_bp.route('/teachers')
@login_required
def teachers():
    """View all teachers."""
    teachers = Teacher.query.all()
    return render_template('admin/teachers.html', teachers=teachers)


@admin_bp.route('/courses')
@login_required
def courses():
    """View and manage courses."""
    courses = Course.query.all()
    branches = Branch.query.all()
    return render_template('admin/courses.html', courses=courses, branches=branches)


@admin_bp.route('/branches')
@login_required
def branches():
    """View and manage branches."""
    branches = Branch.query.all()
    return render_template('admin/branches.html', branches=branches)


@admin_bp.route('/news', methods=['GET', 'POST'])
@login_required
def manage_news():
    """Manage news/announcements."""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        is_active = request.form.get('is_active') == 'on'
        
        news = News(
            title=title,
            content=content,
            author_id=current_user.id,
            is_active=is_active
        )
        db.session.add(news)
        db.session.commit()
        
        flash('โพสต์ข่าวสำเร็จ', 'success')
        return redirect(url_for('admin.manage_news'))
    
    news_list = News.query.order_by(News.published_at.desc()).all()
    return render_template('admin/news.html', news=news_list)
