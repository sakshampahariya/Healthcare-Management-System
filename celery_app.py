"""Celery worker entry: celery -A celery_app.celery worker --loglevel=INFO --pool=solo"""

from app import create_app
from app.extensions import celery

app = create_app()
