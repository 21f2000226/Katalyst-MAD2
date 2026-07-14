import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def ensure_project_root_on_path() -> Path:
    root = str(_PROJECT_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    return _PROJECT_ROOT
