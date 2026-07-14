# Settings. Most stuff can be overridden with env vars / .env
import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or os.environ.get("SECRET_KEY", "dev-key-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB resumes
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 3000))
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"

    # Redis DBs: 0 : cache, 1 :celery broker, 2 : stire celery results
    REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
    REDIS_CONTAINER_NAME = os.environ.get("REDIS_CONTAINER_NAME", "Katalyst-redis")
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://127.0.0.1:6379/1")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/2")

    CACHE_TYPE = os.environ.get("CACHE_TYPE", "RedisCache")
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", "300"))
    CACHE_KEY_PREFIX = os.environ.get("CACHE_KEY_PREFIX", "katalyst_")

    # SMTP for Celery emails (MailHog: 127.0.0.1:1025)
    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    SMTP_FROM = os.environ.get("SMTP_FROM", "katalyst@localhost")
    SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "0").lower() in ("1", "true", "yes")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@placement.local")

    @staticmethod
    def sqlite_uri(instance_path: str) -> str:
        db_path = os.path.join(instance_path, "database.sqlite")
        return f"sqlite:///{db_path.replace(os.sep, '/')}"


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False
