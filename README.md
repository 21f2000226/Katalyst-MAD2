# Katalyst Placement Portal V2

Katalyst is a campus placement portal for institutes, companies, and students. Version 2 uses a decoupled design: a Flask JSON API on the backend and a Vue 3 single-page application on the frontend.

**Author:** Deva Vasista (`21f2000226`)

## What this project does

- **Admin (institute):** Approve companies and placement drives, manage students and companies, view placements, and trigger reminder or report jobs.
- **Company:** Post drives, review applicants and resumes, shortlist or select candidates, and export application CSVs.
- **Student:** Browse approved drives, apply when eligible (including CGPA cutoff), track applications, and manage profile and resume.

Supporting services include JWT auth, Redis caching, Celery background jobs, and local email capture with MailHog.

## Repository layout

```
Katalyst_MAD2/
├── backend/     Flask API, SQLite, Celery, resumes, .env
├── frontend/    Vue 3 + Vite + Bootstrap SPA
└── README.md
```

Work inside `backend/` for API and jobs. Work inside `frontend/` for the UI.

## Prerequisites

| Requirement | Notes |
|-------------|--------|
| Python (conda env such as `mad2_be`) | Backend dependencies from `backend/requirements.txt` |
| Node.js and npm | Frontend dependencies from `frontend/package.json` |
| Redis | Default host port `6379` (for example Docker container `Katalyst-redis`) |
| MailHog (optional but recommended) | SMTP on `1025`, web UI on `8025` |

Copy `backend/.env.example` to `backend/.env` and adjust Redis or SMTP values if needed. The `instance/` folder and SQLite database are created automatically on first run; they are not committed to git.

## Backend

From a terminal:

```powershell
conda activate mad2_be
cd path\to\Katalyst_MAD2\backend
pip install -r requirements.txt
python app.py
```

- API base URL: http://127.0.0.1:3000
- Database file: `backend/instance/database.sqlite`
- Resume uploads: `backend/static/resumes/`

If the database is missing, the app initializes tables and creates the default admin account. To load demo data:

```powershell
python seed_db.py
```

Default admin login: username `admin`, password `password123`.

### Celery worker

Run the worker from `backend/` so background emails and CSV exports can execute:

```powershell
conda activate mad2_be
cd path\to\Katalyst_MAD2\backend
$env:PYTHONPATH = ".."
celery -A backend.workers.celery worker --loglevel=info --pool=solo
```

Optional schedule process (beat):

```powershell
$env:PYTHONPATH = ".."
celery -A backend.workers.celery beat --loglevel=info
```

With MailHog running, open http://localhost:8025 to inspect outgoing mail.

OpenAPI documentation for the JSON API lives in `backend/api.yaml`.

## Frontend

```powershell
cd path\to\Katalyst_MAD2\frontend
npm install
npm run dev
```

The Vite dev server serves the UI at http://localhost:5173 and proxies `/api` requests to Flask on port `3000`.

To build a production bundle that Flask can serve when `frontend/dist` is present:

```powershell
npm run build
```

After building, start only the backend with `python app.py` and open http://127.0.0.1:3000.

Do not commit `node_modules/` or `dist/`. Commit `package.json` and `package-lock.json` so others can install the same frontend dependencies.

## Typical local demo stack

1. Start Redis and MailHog.
2. Start the Flask API (`python app.py` in `backend/`).
3. Start the Celery worker (and beat if you need the crontab schedule).
4. Start the Vue app (`npm run dev` in `frontend/`), or use the Flask-served `dist` build.
5. Log in as admin, company, or student and exercise approvals, applications, and MailHog emails.
