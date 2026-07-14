# Flask entry. Run from backend/: python app.py
from pathlib import Path

from dotenv import load_dotenv

from path_setup import ensure_project_root_on_path

ensure_project_root_on_path()
# load .env : hoping its in the same folder as app.py
load_dotenv(Path(__file__).resolve().parent / ".env")

from backend import create_app
from backend.config import DevConfig
from backend.init_db import initialize_database

app = create_app(DevConfig)


if __name__ == "__main__":
    db_path = Path(app.instance_path) / "database.sqlite"

    # if first run create a db and populate with data, else pass and directly initiliaze
    if not db_path.is_file():
        print(f"No database at {db_path}. Running seed_db.py ...")
        from seed_db import run as seed_database

        seed_database()
        print("Seed complete. Starting server.")
    else:
        with app.app_context():
            initialize_database()

    app.run(host=DevConfig.HOST, port=DevConfig.PORT, debug=DevConfig.DEBUG)
