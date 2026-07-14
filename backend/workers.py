# Celery app and beat schedule config
# From backend/ use commands
#   celery -A backend.workers.celery worker --loglevel=info --pool=solo
#   celery -A backend.workers.celery beat --loglevel=info

import os
import sys
from pathlib import Path

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

_BACKEND_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _BACKEND_DIR.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

load_dotenv(_BACKEND_DIR / ".env", override=True)

# broker/results on Redis DB 1 and 2 (cache uses DB 0)
_redis = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
_broker = os.environ.get("CELERY_BROKER_URL") or _redis.rsplit("/", 1)[0] + "/1"
_backend = os.environ.get("CELERY_RESULT_BACKEND") or _redis.rsplit("/", 1)[0] + "/2"

celery = Celery("katalyst", broker=_broker, backend=_backend, include=["backend.tasks"])

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    # daily reminders and monthly report (times are IST set above)
    beat_schedule={
        "daily-reminders": {
            "task": "backend.tasks.send_daily_reminders",
            "schedule": crontab(hour=14, minute=35),
        },
        "monthly-admin-report": {
            "task": "backend.tasks.send_monthly_admin_report",
            "schedule": crontab(day_of_month=1, hour=8, minute=0),
        },
    },
)


def flask_app():
    load_dotenv(override=True)
    load_dotenv(_BACKEND_DIR / ".env", override=True)
    from backend import create_app

    app = create_app()
    app.config["SMTP_HOST"] = os.environ.get("SMTP_HOST", "")
    app.config["SMTP_PORT"] = int(os.environ.get("SMTP_PORT", "1025"))
    app.config["SMTP_USER"] = os.environ.get("SMTP_USER", "")
    app.config["SMTP_PASSWORD"] = os.environ.get("SMTP_PASSWORD", "")
    app.config["SMTP_FROM"] = os.environ.get("SMTP_FROM", "katalyst@localhost")
    app.config["SMTP_USE_TLS"] = os.environ.get("SMTP_USE_TLS", "0").lower() in ("1", "true", "yes")
    app.config["ADMIN_EMAIL"] = os.environ.get("ADMIN_EMAIL", "admin@placement.local")
    return app
