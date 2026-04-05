# Database Migration and Setup Guide

## 📋 Overview

This directory contains database schemas and migration scripts for the Tutoring School Management System.

## 🗄️ Database Files

- `schema.sql` - Complete database schema for PostgreSQL (production-ready)
- `migrate.py` - Python script to run migrations
- `seed.py` - Script to populate database with initial data

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Start PostgreSQL database
docker-compose up -d db

# Run migrations
python database/migrate.py

# Seed initial data
python database/seed.py
```

### Option 2: Manual Setup

```bash
# Connect to your PostgreSQL database
psql -U username -d tutoring_school

# Run the schema
\i database/schema.sql

# Or from command line
psql -U username -d tutoring_school -f database/schema.sql
```

## 🔧 Configuration

Update your `.env` file with database credentials:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/tutoring_school
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tutoring_school
DB_USER=username
DB_PASSWORD=password
```

## 📊 Database Schema

### Tables

1. **users** - Authentication and user management
2. **parents** - Parent/guardian information
3. **teachers** - Teacher profiles
4. **students** - Student records
5. **branches** - School branch locations
6. **courses** - Course catalog
7. **class_schedule** - Class timetables
8. **enrollments** - Student registrations
9. **payments** - Payment records
10. **attendance** - Attendance tracking
11. **scores** - Student grades
12. **news** - Announcements

### Relationships

```
users (1) ──→ (1) parents
users (1) ──→ (1) teachers
parents (1) ──→ (∞) students
branches (1) ──→ (∞) courses
courses (1) ──→ (∞) class_schedule
teachers (1) ──→ (∞) class_schedule
students (1) ──→ (∞) enrollments
courses (1) ──→ (∞) enrollments
class_schedule (1) ──→ (∞) enrollments
enrollments (1) ──→ (∞) payments
class_schedule (1) ──→ (∞) attendance
students (1) ──→ (∞) attendance
courses (1) ──→ (∞) scores
students (1) ──→ (∞) scores
```

## 🔐 Default Credentials

After running seed data:

- **Email**: admin@tutoring.com
- **Password**: admin123

⚠️ **IMPORTANT**: Change the default admin password immediately after deployment!

## 📈 Reporting Views

The schema includes pre-built views for reporting:

- `v_student_enrollment_summary` - Overview of student enrollments
- `v_payment_summary_by_branch` - Revenue by branch
- `v_attendance_rate_by_student` - Attendance statistics

## 🔄 Migrations

### Creating a New Migration

```bash
# Create a new migration file
cp database/migrations/template.sql database/migrations/002_your_migration_name.sql
```

### Running Migrations

```bash
python database/migrate.py
```

## 💾 Backup & Restore

### Backup

```bash
# Full database backup
pg_dump -U username tutoring_school > backup_$(date +%Y%m%d).sql

# Backup specific table
pg_dump -U username -t users tutoring_school > users_backup.sql
```

### Restore

```bash
psql -U username tutoring_school < backup_20240101.sql
```

## 🔒 Security Best Practices

1. **Use environment variables** for database credentials
2. **Enable SSL/TLS** for database connections in production
3. **Regular backups** - Set up automated daily backups
4. **Connection pooling** - Use PgBouncer for high-traffic deployments
5. **Limit database user permissions** - Follow principle of least privilege
6. **Audit logging** - Enable PostgreSQL audit extensions

## 📊 Performance Optimization

### Indexes

All foreign keys and frequently queried columns are indexed:

- Email addresses
- User roles
- Status fields
- Date fields
- Foreign key relationships

### Query Optimization

Use the provided views for common reports instead of writing complex joins.

### Connection Pooling

For production, configure connection pooling in your application:

```python
# In config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
```

## 🐛 Troubleshooting

### Connection Issues

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check logs
docker logs tutoring-school-db-1
```

### Migration Errors

```bash
# Reset database (DEVELOPMENT ONLY)
psql -U username -c "DROP DATABASE tutoring_school;"
psql -U username -c "CREATE DATABASE tutoring_school;"
python database/migrate.py
```

## 📚 Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)

## 🆘 Support

For issues or questions, please check:
1. Application logs in `/logs` directory
2. Database logs
3. Error messages in migration output
