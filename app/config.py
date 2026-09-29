import os

from dotenv import load_dotenv
from sqlalchemy.pool import StaticPool

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", os.getenv("JWT_SECRET_KEY", "dev-secret"))
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/diagnostic_booking",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
    CELERY_TASK_ALWAYS_EAGER = os.getenv("CELERY_TASK_ALWAYS_EAGER", "false").lower() in {
        "1",
        "true",
        "yes",
    }

    PAYMENT_SIMULATE_RESULT = os.getenv("PAYMENT_SIMULATE_RESULT", "SUCCESS")
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "60"))
    USE_FAKEREDIS = False
    JSON_SORT_KEYS = False

    # ── Flask-Mail ────────────────────────────────────────────────────────────
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() in {"1", "true", "yes"}
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() in {"1", "true", "yes"}
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)
    MAIL_SUPPRESS_SEND = os.getenv("MAIL_SUPPRESS_SEND", "false").lower() in {"1", "true", "yes"}


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    _test_db = os.getenv("TEST_DATABASE_URL", "sqlite://")
    SQLALCHEMY_DATABASE_URI = _test_db
    SQLALCHEMY_ENGINE_OPTIONS = (
        {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }
        if _test_db.startswith("sqlite")
        else {"pool_pre_ping": True}
    )
    JWT_SECRET_KEY = "test-jwt-secret"
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_BROKER_URL = "memory://"
    CELERY_RESULT_BACKEND = "cache+memory://"
    USE_FAKEREDIS = True
    PAYMENT_SIMULATE_RESULT = "SUCCESS"
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True  # never send real emails during tests
    MAIL_DEFAULT_SENDER = "noreply@evehealthcare.com"  # must be non-empty for Flask-Mail


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
