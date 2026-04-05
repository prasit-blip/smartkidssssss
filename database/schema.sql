-- ================================================================
-- Tutoring School Management System - Database Schema
-- Production Ready SQL Schema for PostgreSQL/MySQL
-- ================================================================

-- Drop tables if exist (for clean installation)
-- Execute in reverse order of dependencies

DROP TABLE IF EXISTS news CASCADE;
DROP TABLE IF EXISTS scores CASCADE;
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS enrollments CASCADE;
DROP TABLE IF EXISTS class_schedule CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS branches CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS teachers CASCADE;
DROP TABLE IF EXISTS parents CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ================================================================
-- 1. USERS TABLE - Authentication & Authorization
-- ================================================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- 'admin', 'parent', 'teacher'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);

-- ================================================================
-- 2. PARENTS TABLE - Parent/Guardian Information
-- ================================================================
CREATE TABLE parents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    line_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_parents_user_id ON parents(user_id);

-- ================================================================
-- 3. TEACHERS TABLE - Teacher Information
-- ================================================================
CREATE TABLE teachers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    specialization VARCHAR(100),  -- Math, English, Science
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_teachers_user_id ON teachers(user_id);

-- ================================================================
-- 4. STUDENTS TABLE - Student Information
-- ================================================================
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER NOT NULL REFERENCES parents(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    school VARCHAR(200),
    grade_level VARCHAR(20) NOT NULL,  -- ป.1 - ป.6
    date_of_birth DATE,
    profile_image VARCHAR(256),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_students_parent_id ON students(parent_id);
CREATE INDEX idx_students_grade_level ON students(grade_level);

-- ================================================================
-- 5. BRANCHES TABLE - School Branch Locations
-- ================================================================
CREATE TABLE branches (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    opening_hours VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_branches_is_active ON branches(is_active);

-- ================================================================
-- 6. COURSES TABLE - Course Catalog
-- ================================================================
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    branch_id INTEGER NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    subject VARCHAR(50) NOT NULL,  -- Math, English, Science
    name VARCHAR(200) NOT NULL,
    grade_level VARCHAR(20) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    total_hours INTEGER NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_courses_branch_id ON courses(branch_id);
CREATE INDEX idx_courses_subject ON courses(subject);
CREATE INDEX idx_courses_grade_level ON courses(grade_level);
CREATE INDEX idx_courses_is_active ON courses(is_active);

-- ================================================================
-- 7. CLASS_SCHEDULE TABLE - Class Timetable
-- ================================================================
CREATE TABLE class_schedule (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    branch_id INTEGER NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    day_of_week VARCHAR(20) NOT NULL,  -- Monday, Tuesday, etc.
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    room_number VARCHAR(50),
    max_students INTEGER DEFAULT 20,
    is_recurring BOOLEAN DEFAULT TRUE,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_class_schedule_course_id ON class_schedule(course_id);
CREATE INDEX idx_class_schedule_branch_id ON class_schedule(branch_id);
CREATE INDEX idx_class_schedule_teacher_id ON class_schedule(teacher_id);
CREATE INDEX idx_class_schedule_day_of_week ON class_schedule(day_of_week);

-- ================================================================
-- 8. ENROLLMENTS TABLE - Student Course Registrations
-- ================================================================
CREATE TABLE enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    parent_id INTEGER NOT NULL REFERENCES parents(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    class_id INTEGER NOT NULL REFERENCES class_schedule(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, cancelled
    enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX idx_enrollments_parent_id ON enrollments(parent_id);
CREATE INDEX idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX idx_enrollments_class_id ON enrollments(class_id);
CREATE INDEX idx_enrollments_status ON enrollments(status);

-- ================================================================
-- 9. PAYMENTS TABLE - Payment Records
-- ================================================================
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    enrollment_id INTEGER NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
    parent_id INTEGER NOT NULL REFERENCES parents(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50),  -- bank_transfer, qrcode, online
    status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected
    slip_filename VARCHAR(256),
    transfer_date TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_enrollment_id ON payments(enrollment_id);
CREATE INDEX idx_payments_parent_id ON payments(parent_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_created_at ON payments(created_at);

-- ================================================================
-- 10. ATTENDANCE TABLE - Attendance Tracking
-- ================================================================
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL REFERENCES class_schedule(id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    attendance_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,  -- present, absent, late, leave
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    checked_by INTEGER REFERENCES users(id),
    notes TEXT
);

CREATE INDEX idx_attendance_class_id ON attendance(class_id);
CREATE INDEX idx_attendance_student_id ON attendance(student_id);
CREATE INDEX idx_attendance_date ON attendance(attendance_date);
CREATE INDEX idx_attendance_status ON attendance(status);

-- ================================================================
-- 11. SCORES TABLE - Student Grades/Scores
-- ================================================================
CREATE TABLE scores (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    score_value DECIMAL(5, 2) NOT NULL,
    max_score DECIMAL(5, 2) DEFAULT 100,
    test_name VARCHAR(200),
    test_date DATE,
    notes TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scores_student_id ON scores(student_id);
CREATE INDEX idx_scores_course_id ON scores(course_id);
CREATE INDEX idx_scores_created_at ON scores(created_at);

-- ================================================================
-- 12. NEWS TABLE - News & Announcements
-- ================================================================
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER REFERENCES users(id),
    published_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_news_published_at ON news(published_at);
CREATE INDEX idx_news_is_active ON news(is_active);

-- ================================================================
-- SEED DATA - Initial Data for Testing
-- ================================================================

-- Insert Admin User (password: admin123)
INSERT INTO users (email, password_hash, role, is_active) VALUES
('admin@tutoring.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', 'admin', TRUE);

-- Insert a Branch
INSERT INTO branches (name, address, phone, opening_hours, is_active) VALUES
('สาขาหลัก - สุขุมวิท', '123 ถนนสุขุมวิท กรุงเทพฯ', '02-123-4567', '09:00-20:00', TRUE),
('สาขาเชียงใหม่', '456 ถนนช้างคลาน เชียงใหม่', '053-123-456', '09:00-19:00', TRUE);

-- Insert Sample Courses
INSERT INTO courses (branch_id, subject, name, grade_level, price, total_hours, description, is_active) VALUES
(1, 'คณิตศาสตร์', 'คณิตศาสตร์พื้นฐาน ป.1', 'ป.1', 2500.00, 20, 'เรียนคณิตศาสตร์พื้นฐานสำหรับนักเรียนชั้นประถมศึกษาปีที่ 1', TRUE),
(1, 'ภาษาอังกฤษ', 'ภาษาอังกฤษสื่อสาร ป.2', 'ป.2', 2800.00, 20, 'พัฒนาทักษะการสื่อสารภาษาอังกฤษ', TRUE),
(1, 'วิทยาศาสตร์', 'วิทยาศาสตร์สนุกๆ ป.3', 'ป.3', 2600.00, 20, 'เรียนรู้วิทยาศาสตร์ผ่านการทดลอง', TRUE),
(2, 'คณิตศาสตร์', 'คณิตศาสตร์ขั้นสูง ป.4', 'ป.4', 2700.00, 20, 'เตรียมความพร้อมสำหรับคณิตศาสตร์ระดับสูง', TRUE);

-- ================================================================
-- VIEWS FOR REPORTING
-- ================================================================

-- View: Student Enrollment Summary
CREATE OR REPLACE VIEW v_student_enrollment_summary AS
SELECT 
    s.id as student_id,
    s.first_name || ' ' || s.last_name as student_name,
    s.grade_level,
    p.first_name || ' ' || p.last_name as parent_name,
    c.name as course_name,
    c.subject,
    e.status as enrollment_status,
    e.enrolled_at
FROM students s
JOIN parents p ON s.parent_id = p.id
JOIN enrollments e ON s.id = e.student_id
JOIN courses c ON e.course_id = c.id;

-- View: Payment Summary by Branch
CREATE OR REPLACE VIEW v_payment_summary_by_branch AS
SELECT 
    b.name as branch_name,
    COUNT(p.id) as total_payments,
    SUM(CASE WHEN p.status = 'approved' THEN p.amount ELSE 0 END) as total_revenue,
    SUM(CASE WHEN p.status = 'pending' THEN p.amount ELSE 0 END) as pending_revenue
FROM branches b
LEFT JOIN courses c ON b.id = c.branch_id
LEFT JOIN enrollments e ON c.id = e.course_id
LEFT JOIN payments p ON e.id = p.enrollment_id
GROUP BY b.name;

-- View: Attendance Rate by Student
CREATE OR REPLACE VIEW v_attendance_rate_by_student AS
SELECT 
    s.id as student_id,
    s.first_name || ' ' || s.last_name as student_name,
    COUNT(a.id) as total_classes,
    COUNT(CASE WHEN a.status = 'present' THEN 1 END) as present_count,
    ROUND(COUNT(CASE WHEN a.status = 'present' THEN 1 END)::NUMERIC / COUNT(a.id)::NUMERIC * 100, 2) as attendance_rate
FROM students s
LEFT JOIN attendance a ON s.id = a.student_id
GROUP BY s.id, s.first_name, s.last_name;

-- ================================================================
-- FUNCTIONS & TRIGGERS
-- ================================================================

-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger: Auto-update updated_at on users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ================================================================
-- PERMISSIONS (For PostgreSQL)
-- ================================================================
-- Note: Adjust according to your database user setup

-- Create application user (optional)
-- CREATE USER tutoring_app WITH PASSWORD 'your_secure_password';
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tutoring_app;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO tutoring_app;

-- ================================================================
-- NOTES FOR PRODUCTION DEPLOYMENT
-- ================================================================
-- 1. Change default admin password immediately after deployment
-- 2. Use environment variables for database credentials
-- 3. Enable SSL/TLS for database connections
-- 4. Set up regular database backups
-- 5. Monitor database performance and optimize indexes
-- 6. Implement connection pooling for better performance
-- 7. Review and adjust max_connections based on expected load
-- ================================================================
