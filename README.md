# ระบบเว็บไซต์โรงเรียนติวเด็กประถม (Tutoring School Management System)

ระบบจัดการโรงเรียนติวสำหรับเด็กประถมแบบครบวงจร พัฒนาด้วย Python Flask

## 🎯 ฟีเจอร์หลัก

- 🔐 ระบบสมาชิก (Authentication & Authorization)
- 👥 จัดการนักเรียน / ผู้ปกครอง / ครู
- 🏫 รองรับหลายสาขา (Multi-Branch)
- 📚 ระบบคอร์สเรียนและตารางเรียน
- 📝 ระบบลงทะเบียนเรียน
- 💳 ระบบชำระเงินพร้อมอัปโหลดสลิป
- 📍 ระบบเช็คอินเรียน
- 📊 ระบบผลการเรียน
- 🔔 ระบบแจ้งเตือน
- 📈 Dashboard สำหรับ Admin

## 🚀 การติดตั้งสำหรับ Production

### วิธีที่ 1: ใช้ Docker (แนะนำ)

```bash
# คัดลอกไฟล์ environment
cp .env.example .env

# แก้ไขค่าในไฟล์ .env ให้เหมาะสม
nano .env

# Build และรัน Docker containers
docker-compose up -d --build

# ดู logs
docker-compose logs -f
```

### วิธีที่ 2: ติดตั้งบน VPS โดยตรง

```bash
# ติดตั้ง dependencies ของระบบ
sudo apt update
sudo apt install -y python3-pip python3-venv postgresql nginx

# สร้าง virtual environment
python3 -m venv venv
source venv/bin/activate

# ติดตั้ง Python packages
pip install -r requirements.txt

# ตั้งค่า PostgreSQL
sudo -u postgres psql
CREATE DATABASE tutoring_school;
CREATE USER tutor_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE tutoring_school TO tutor_user;
\q

# ตั้งค่า environment variables
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="postgresql://tutor_user:your_password@localhost/tutoring_school"
export FLASK_ENV=production

# รัน migrations
flask db upgrade

# รันด้วย Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 wsgi:app
```

## 📁 โครงสร้างโปรเจกต์

```
/workspace
├── app/                      # Application package
│   ├── __init__.py          # Application factory
│   ├── models/              # Database models
│   ├── blueprints/          # Flask blueprints
│   │   ├── auth.py         # Authentication routes
│   │   ├── parent.py       # Parent routes
│   │   ├── teacher.py      # Teacher routes
│   │   ├── admin.py        # Admin routes
│   │   └── api.py          # API endpoints
│   └── routes/              # Additional routes
├── static/                   # Static files
│   └── uploads/             # Uploaded files
├── templates/                # HTML templates
├── config.py                 # Configuration settings
├── wsgi.py                   # WSGI entry point
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose configuration
└── nginx.conf                # Nginx configuration
```

## 🔐 การตั้งค่า Security

1. เปลี่ยน `SECRET_KEY` ในไฟล์ `.env` เป็นค่าที่ซับซ้อน
2. ใช้ HTTPS ใน production
3. เปิดใช้ rate limiting
4. ตรวจสอบ file uploads อย่างเข้มงวด

## 📊 Database Migration

```bash
# Initialize migrations (ทำครั้งเดียว)
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 👤 บัญชีเริ่มต้น (หลังสร้าง sample data)

- **Admin**: admin@school.com / admin123

## 📝 License

MIT License
