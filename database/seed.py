#!/usr/bin/env python3
"""
Database Seed Script for Tutoring School Management System.

This script populates the database with initial test data.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, date, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models import User, Parent, Teacher, Student, Branch, Course, Class, Enrollment


def seed_database():
    """Populate database with initial data."""
    app = create_app()
    
    with app.app_context():
        print("🌱 Starting database seeding...")
        
        try:
            # Check if data already exists
            if User.query.filter_by(email='admin@tutoring.com').first():
                print("⚠️  Database already seeded. Use --force to reseed.")
                return
            
            # Create Admin User
            print("👤 Creating admin user...")
            admin = User(
                email='admin@tutoring.com',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create Sample Parent User
            print("👨‍👩‍👧 Creating parent user...")
            parent_user = User(
                email='parent@example.com',
                role='parent',
                is_active=True
            )
            parent_user.set_password('parent123')
            db.session.add(parent_user)
            db.session.flush()
            
            parent = Parent(
                user_id=parent_user.id,
                first_name='สมชาย',
                last_name='รักลูก',
                phone='081-234-5678',
                address='123 ถนนสุขุมวิท กรุงเทพฯ',
                line_id='parent_line'
            )
            db.session.add(parent)
            db.session.flush()
            
            # Create Sample Teacher
            print("👨‍🏫 Creating teacher...")
            teacher_user = User(
                email='teacher@tutoring.com',
                role='teacher',
                is_active=True
            )
            teacher_user.set_password('teacher123')
            db.session.add(teacher_user)
            db.session.flush()
            
            teacher = Teacher(
                user_id=teacher_user.id,
                first_name='ครูสมศักดิ์',
                last_name='สอนเก่ง',
                phone='089-876-5432',
                specialization='คณิตศาสตร์'
            )
            db.session.add(teacher)
            db.session.flush()
            
            # Create Students
            print("👶 Creating students...")
            student1 = Student(
                parent_id=parent.id,
                first_name='ด.ช.เรียนดี',
                last_name='รักลูก',
                school='โรงเรียนสาธิต',
                grade_level='ป.3',
                date_of_birth=date(2015, 5, 15)
            )
            student2 = Student(
                parent_id=parent.id,
                first_name='ด.ญ.เรียนเก่ง',
                last_name='รักลูก',
                school='โรงเรียนสาธิต',
                grade_level='ป.1',
                date_of_birth=date(2017, 8, 20)
            )
            db.session.add_all([student1, student2])
            db.session.flush()
            
            # Get branches (should already exist from schema seed)
            branches = Branch.query.all()
            if not branches:
                print("🏫 Creating branches...")
                branch1 = Branch(
                    name='สาขาหลัก - สุขุมวิท',
                    address='123 ถนนสุขุมวิท กรุงเทพฯ',
                    phone='02-123-4567',
                    opening_hours='09:00-20:00',
                    is_active=True
                )
                branch2 = Branch(
                    name='สาขาเชียงใหม่',
                    address='456 ถนนช้างคลาน เชียงใหม่',
                    phone='053-123-456',
                    opening_hours='09:00-19:00',
                    is_active=True
                )
                db.session.add_all([branch1, branch2])
                db.session.flush()
                branches = [branch1, branch2]
            
            # Get teachers
            teachers = Teacher.query.all()
            if not teachers:
                print("⚠️  No teachers found. Please run migration first.")
                return
            
            # Create Courses
            print("📚 Creating courses...")
            courses_data = [
                {'subject': 'คณิตศาสตร์', 'name': 'คณิตศาสตร์พื้นฐาน ป.1', 'grade_level': 'ป.1', 'price': 2500.00, 'total_hours': 20, 'description': 'เรียนคณิตศาสตร์พื้นฐานสำหรับนักเรียนชั้นประถมศึกษาปีที่ 1'},
                {'subject': 'ภาษาอังกฤษ', 'name': 'ภาษาอังกฤษสื่อสาร ป.2', 'grade_level': 'ป.2', 'price': 2800.00, 'total_hours': 20, 'description': 'พัฒนาทักษะการสื่อสารภาษาอังกฤษ'},
                {'subject': 'วิทยาศาสตร์', 'name': 'วิทยาศาสตร์สนุกๆ ป.3', 'grade_level': 'ป.3', 'price': 2600.00, 'total_hours': 20, 'description': 'เรียนรู้วิทยาศาสตร์ผ่านการทดลอง'},
                {'subject': 'คณิตศาสตร์', 'name': 'คณิตศาสตร์ขั้นสูง ป.4', 'grade_level': 'ป.4', 'price': 2700.00, 'total_hours': 20, 'description': 'เตรียมความพร้อมสำหรับคณิตศาสตร์ระดับสูง'},
                {'subject': 'ภาษาอังกฤษ', 'name': 'ภาษาอังกฤษเพื่อสอบ ป.5', 'grade_level': 'ป.5', 'price': 3000.00, 'total_hours': 24, 'description': 'เตรียมตัวสอบภาษาอังกฤษ'},
                {'subject': 'วิทยาศาสตร์', 'name': 'วิทย์-คณิต ป.6', 'grade_level': 'ป.6', 'price': 3200.00, 'total_hours': 24, 'description': 'เตรียมสอบเข้ามัธยม'},
            ]
            
            courses = []
            for i, course_data in enumerate(courses_data):
                branch = branches[i % len(branches)]
                course = Course(
                    branch_id=branch.id,
                    subject=course_data['subject'],
                    name=course_data['name'],
                    grade_level=course_data['grade_level'],
                    price=course_data['price'],
                    total_hours=course_data['total_hours'],
                    description=course_data['description'],
                    is_active=True
                )
                courses.append(course)
                db.session.add(course)
            
            db.session.flush()
            
            # Create Class Schedules
            print("📅 Creating class schedules...")
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            classes = []
            for i, course in enumerate(courses[:4]):  # Create classes for first 4 courses
                teacher = teachers[0]
                branch = Branch.query.get(course.branch_id)
                
                class_schedule = Class(
                    course_id=course.id,
                    branch_id=branch.id,
                    teacher_id=teacher.id,
                    day_of_week=days[i % 7],
                    start_time=datetime.strptime('10:00', '%H:%M').time(),
                    end_time=datetime.strptime('12:00', '%H:%M').time(),
                    room_number=f'Room {i+1}',
                    max_students=20,
                    is_recurring=True,
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=90)
                )
                classes.append(class_schedule)
                db.session.add(class_schedule)
            
            db.session.flush()
            
            # Create Enrollments
            print("📝 Creating enrollments...")
            if classes and courses:
                enrollment = Enrollment(
                    student_id=student1.id,
                    parent_id=parent.id,
                    course_id=courses[2].id,  # Science for ป.3
                    class_id=classes[2].id if len(classes) > 2 else classes[0].id,
                    status='approved'
                )
                db.session.add(enrollment)
            
            # Commit all changes
            db.session.commit()
            
            print("\n✨ Database seeded successfully!")
            print("\n📋 Test Credentials:")
            print("   👨‍💼 Admin:")
            print("      Email: admin@tutoring.com")
            print("      Password: admin123")
            print("\n   👨‍👩‍👧 Parent:")
            print("      Email: parent@example.com")
            print("      Password: parent123")
            print("\n   👨‍🏫 Teacher:")
            print("      Email: teacher@tutoring.com")
            print("      Password: teacher123")
            print("\n⚠️  IMPORTANT: Change all default passwords after first login!")
            
        except Exception as e:
            print(f"\n❌ Seeding failed: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    force = '--force' in sys.argv
    if force:
        print("⚠️  Force seeding requested. Existing data may be duplicated.")
    
    seed_database()
