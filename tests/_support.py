from __future__ import annotations

import sys
from pathlib import Path


def import_scripts() -> None:
    scripts = Path(__file__).parents[1] / ".github" / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
