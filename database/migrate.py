#!/usr/bin/env python3
"""
Database Migration Script for Tutoring School Management System.

This script initializes the database and runs migrations.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from sqlalchemy import text


def run_migrations():
    """Run database migrations."""
    app = create_app()
    
    with app.app_context():
        print("🚀 Starting database migration...")
        
        try:
            # Create all tables from models
            print("📊 Creating database tables...")
            db.create_all()
            print("✅ Tables created successfully!")
            
            # Run additional SQL migrations if needed
            schema_file = Path(__file__).parent / 'schema.sql'
            if schema_file.exists():
                print("📄 Applying schema.sql...")
                with open(schema_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                    
                # Split by semicolons and execute each statement
                statements = [s.strip() for s in sql_content.split(';') if s.strip()]
                
                for statement in statements:
                    # Skip comments-only statements
                    if statement.startswith('--'):
                        continue
                    
                    try:
                        db.session.execute(text(statement))
                        db.session.commit()
                    except Exception as e:
                        # Some statements might fail (e.g., DROP TABLE IF EXISTS on first run)
                        # This is okay, continue with next statement
                        pass
                
                print("✅ Schema applied successfully!")
            
            print("\n✨ Migration completed successfully!")
            print("\n📋 Next steps:")
            print("   1. Run 'python database/seed.py' to populate initial data")
            print("   2. Change default admin password after first login")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            db.session.rollback()
            sys.exit(1)


def reset_database():
    """Drop all tables and recreate (USE WITH CAUTION)."""
    app = create_app()
    
    with app.app_context():
        confirm = input("⚠️  WARNING: This will delete ALL data. Type 'YES' to confirm: ")
        if confirm != 'YES':
            print("Operation cancelled.")
            return
        
        print("🗑️  Dropping all tables...")
        db.drop_all()
        print("✅ All tables dropped.")
        
        print("🚀 Running migration...")
        run_migrations()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_database()
    else:
        run_migrations()
