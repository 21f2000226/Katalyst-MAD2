from datetime import datetime

from backend.auth.utils import clean, to_float, to_int

#parse dates / job fields coming from JSON forms. For Database integrity
def parse_deadline(value) -> datetime | None:
    # accepts YYYY-MM-DD or full ISO. datetime-local sends YYYY-MM-DDTHH:MM
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    for fmt in (
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    ):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def parse_interview_at(value) -> datetime | None:
    return parse_deadline(value)


def parse_joining_date(value):
    from datetime import date

    if not value:
        return None
    if isinstance(value, date):
        return value
    text = str(value).strip()
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        return None


def job_position_from_json(data: dict) -> dict:
    # pull drive fields out of a request body
    min_cgpa = to_float(data.get("min_cgpa"))
    if min_cgpa is not None and min_cgpa <= 0:
        min_cgpa = None
    return {
        "title": clean(data.get("title")),
        "description": clean(data.get("description")) or None,
        "requirements": clean(data.get("requirements")) or None,
        "min_cgpa": min_cgpa,
        "salary_min": to_int(data.get("salary_min")),
        "salary_max": to_int(data.get("salary_max")),
        "deadline": parse_deadline(data.get("deadline")),
    }
