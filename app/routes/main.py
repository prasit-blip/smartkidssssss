"""
Main Routes Blueprint for the Tutoring School Management System.

Handles public-facing pages like home, courses, and about.
"""

from flask import Blueprint, render_template
from app.models import News, Branch, Course

main_bp = Blueprint('main', __name__, template_folder='../../templates')


@main_bp.route('/')
def index():
    """Home page."""
    news = News.query.filter_by(is_active=True).order_by(News.published_at.desc()).limit(5).all()
    branches = Branch.query.filter_by(is_active=True).all()
    return render_template('index.html', news=news, branches=branches)


@main_bp.route('/courses')
def courses():
    """Course listing page."""
    courses = Course.query.filter_by(is_active=True).all()
    branches = Branch.query.filter_by(is_active=True).all()
    return render_template('courses.html', courses=courses, branches=branches)


@main_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return {'status': 'healthy'}, 200
