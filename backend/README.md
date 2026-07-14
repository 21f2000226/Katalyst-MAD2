# Katalyst backend

Flask JSON API, JWT authentication and authorization, includes Redis cache, Celery jobs, and SQLite DB.

## Run (from this folder)

```powershell
conda activate mad2_be
pip install -r requirements.txt
python app.py
```

```powershell
python seed_db.py
```

```powershell
$env:PYTHONPATH = ".."
celery -A backend.workers.celery worker --loglevel=info --pool=solo
```

Config: `.env` (see `.env.example`).  
Database: `instance/database.sqlite`  
Uploads: `static/resumes/`
