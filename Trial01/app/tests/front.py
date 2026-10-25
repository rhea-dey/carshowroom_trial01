"""Compatibility launcher for the current car showroom application."""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.front import root


if __name__ == "__main__":
    root.mainloop()
