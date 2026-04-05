"""
Authentication Blueprint for the Tutoring School Management System.

Handles user registration, login, logout, and password management.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Parent

auth_bp = Blueprint('auth', __name__, template_folder='../../templates')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('routes.main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        
        # Validation
        if password != confirm_password:
            flash('รหัสผ่านไม่ตรงกัน', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('อีเมลนี้ถูกใช้งานแล้ว', 'error')
            return render_template('register.html')
        
        # Create user
        user = User(email=email, role='parent')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Create parent profile
        parent = Parent(
            user_id=user.id,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        db.session.add(parent)
        db.session.commit()
        
        flash('สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('routes.main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('บัญชีผู้ใช้ถูกระงับ กรุณาติดต่อผู้ดูแลระบบ', 'error')
                return render_template('login.html')
            
            login_user(user, remember=bool(remember))
            next_page = request.args.get('next')
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(next_page or url_for('admin.dashboard'))
            elif user.role == 'teacher':
                return redirect(next_page or url_for('teacher.dashboard'))
            else:
                return redirect(next_page or url_for('parent.dashboard'))
        else:
            flash('อีเมลหรือรหัสผ่านไม่ถูกต้อง', 'error')
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('ออกจากระบบเรียบร้อยแล้ว', 'success')
    return redirect(url_for('routes.main.index'))
