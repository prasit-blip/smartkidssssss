"""
WSGI entry point for the Tutoring School Management System.

This file is used by Gunicorn to serve the application in production.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
