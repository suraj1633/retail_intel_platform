"""Project-wide runtime settings and defaults."""

from __future__ import annotations

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.getenv("DB_PATH", os.path.join(DATABASE_DIR, "db.sqlite"))

DEFAULT_PLATFORM_MAP = {
    "Newegg US": "newegg",
    "Mercado Libre BR": "mercadolivre",
}

DEFAULT_BRANDS = ["Intel", "AMD", "Qualcomm", "Apple"]

DEFAULT_AUDIT_WEIGHTS = {
    "Notebook": 0.85,
    "Desktop": 0.15,
}

os.makedirs(DATABASE_DIR, exist_ok=True)
