"""
API Blueprint for the Tutoring School Management System.

Provides RESTful API endpoints for external integrations and mobile apps.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Parent, Student, Course, Class, Enrollment

api_bp = Blueprint('api', __name__)


@api_bp.route('/students', methods=['GET'])
@login_required
def get_students():
    """Get students for the current parent."""
    parent = Parent.query.filter_by(user_id=current_user.id).first_or_404()
    students = Student.query.filter_by(parent_id=parent.id).all()

    return jsonify([{
        'id': s.id,
        'first_name': s.first_name,
        'last_name': s.last_name,
        'grade_level': s.grade_level,
        'school': s.school
    } for s in students])


@api_bp.route('/courses', methods=['GET'])
@login_required
def get_courses():
    """Get all active courses."""
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
    
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'subject': c.subject,
        'grade_level': c.grade_level,
        'price': c.price,
        'total_hours': c.total_hours,
        'branch_id': c.branch_id
    } for c in courses])


@api_bp.route('/enroll', methods=['POST'])
@login_required
def create_enrollment():
    """Create a new enrollment."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['student_id', 'course_id', 'class_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    parent = Parent.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Check if enrollment already exists
    existing = Enrollment.query.filter_by(
        student_id=data['student_id'],
        course_id=data['course_id'],
        class_id=data['class_id'],
        status='pending'
    ).first()
    
    if existing:
        return jsonify({'error': 'Enrollment already exists'}), 409
    
    enrollment = Enrollment(
        student_id=data['student_id'],
        parent_id=parent.id,
        course_id=data['course_id'],
        class_id=data['class_id'],
        status='pending'
    )
    db.session.add(enrollment)
    db.session.commit()

    return jsonify({
        'message': 'Enrollment created successfully',
        'enrollment_id': enrollment.id
    }), 201


@api_bp.route('/enrollments', methods=['GET'])
@login_required
def get_enrollments():
    """Get enrollments for the current parent."""
    parent = Parent.query.filter_by(user_id=current_user.id).first_or_404()
    enrollments = Enrollment.query.filter_by(parent_id=parent.id)\
        .order_by(Enrollment.enrolled_at.desc()).all()

    return jsonify([{
        'id': e.id,
        'student_id': e.student_id,
        'course_id': e.course_id,
        'class_id': e.class_id,
        'status': e.status,
        'enrolled_at': e.enrolled_at.isoformat()
    } for e in enrollments])
