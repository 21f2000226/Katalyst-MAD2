# Katalyst - Placement Portal V2

Flask JSON API + Vue SPA (MAD2). High-level layout:

```
Katalyst_MAD2/
├── backend/     # Flask API, Celery, SQLite, resumes, .env
├── frontend/    # Vue 3 + Vite + Bootstrap
└── README.md
```

Work **inside** each folder for that side of the stack.

**Author:** Deva Vasista (21f2000226)

---

## Prerequisites

| Service | Ports |
|---------|-------|
| Redis (`Katalyst-redis`) | `6379` |
| MailHog | SMTP `1025`, UI `8025` |
| conda env  | backend Python |
| Node.js | frontend |

---

## Backend (`cd backend`)

```powershell
conda activate mad2_be
cd E:\MAD2\Katalyst_MAD2\backend
pip install -r requirements.txt
# copy .env.example to .env if needed
python app.py
```

API: http://127.0.0.1:3000  
DB: `backend/instance/database.sqlite`  
Resumes: `backend/static/resumes/`

Seed demo data (from `backend/`):

```powershell
python seed_db.py
```

Default admin: `admin` / `password123`

### Celery (also from `backend/`)

```powershell
conda activate mad2_be
cd E:\MAD2\Katalyst_MAD2\backend
$env:PYTHONPATH = ".."
celery -A backend.workers.celery worker --loglevel=info --pool=solo
```

Optional beat:

```powershell
$env:PYTHONPATH = ".."
celery -A backend.workers.celery beat --loglevel=info
```

MailHog UI: http://localhost:8025

---

## Frontend (`cd frontend`)

```powershell
cd E:\MAD2\Katalyst_MAD2\frontend
npm install
npm run dev
```

UI: http://localhost:5173 (proxies `/api` to Flask `:3000`)

Production build (served by Flask when present):

```powershell
npm run build
```

Then only `python app.py` in `backend/` is needed; open http://127.0.0.1:3000

---