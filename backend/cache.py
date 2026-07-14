from flask import jsonify

from backend.extensions import flask_cache

JOBS_VERSION_KEY = "katalyst:jobs_version"
ADMIN_VERSION_KEY = "katalyst:admin_version"

# Cache functions : Redis helpers. We bump a version number instead of deleting every key


def _version(key: str) -> int:
    value = flask_cache.get(key)
    try:
        return int(value) if value is not None else 0
    except (TypeError, ValueError):
        return 0


def _bump(key: str) -> None:
    # timeout=0 so the version counter itself never expires
    flask_cache.set(key, _version(key) + 1, timeout=0)


def invalidate_job_related_caches() -> None:
    # job/company changed then  public lists and admin dashboard stale
    _bump(JOBS_VERSION_KEY)
    _bump(ADMIN_VERSION_KEY)


def invalidate_admin_caches() -> None:
    _bump(ADMIN_VERSION_KEY)


def public_jobs_list_key(search_q: str | None) -> str:
    q = (search_q or "").strip().lower() or "all"
    return f"katalyst:public:jobs:list:v{_version(JOBS_VERSION_KEY)}:{q}"


def public_job_detail_key(job_id: int) -> str:
    return f"katalyst:public:jobs:detail:v{_version(JOBS_VERSION_KEY)}:{job_id}"


def public_company_detail_key(company_id: int) -> str:
    return f"katalyst:public:companies:detail:v{_version(JOBS_VERSION_KEY)}:{company_id}"


def admin_dashboard_key(search_q: str | None) -> str:
    q = (search_q or "").strip().lower() or "all"
    return f"katalyst:admin:dashboard:v{_version(ADMIN_VERSION_KEY)}:{q}"


def cached_json(key: str):
    # HIT -> return jsonify with X-Cache header. MISS -> None
    payload = flask_cache.get(key)
    if payload is None:
        return None
    response = jsonify(payload)
    response.headers["X-Cache"] = "HIT"
    return response


def store_json(key: str, payload: dict):
    flask_cache.set(key, payload)
    response = jsonify(payload)
    response.headers["X-Cache"] = "MISS"
    return response
