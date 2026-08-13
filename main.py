"""
main.py
Application Entry Point.
Launches the Streamlit dashboard using existing local database data.
"""

import os
import subprocess
import sys

from database.db_manager import init_db
from engine.data_pipeline import seed_compliance_and_shelf_data


def main():
    print("--- Starting Retail Intelligence Platform ---")

    init_db()
    try:
        seed_result = seed_compliance_and_shelf_data()
        print(f"[App] Database ready. Seeded {seed_result.get('products', 0)} product rows.")
    except Exception as exc:
        print(f"[App] Seed check skipped: {exc}")

    app_script = os.path.join("dashboard", "app.py")

    if not os.path.exists(app_script):
        print(f"[Error] Streamlit file '{app_script}' not found.")
        return

    print(f"[App] Launching Retail Intel Dashboard from '{app_script}'...")

    cmd = [sys.executable, "-m", "streamlit", "run", app_script]

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n[App] Dashboard stopped by user.")
    except Exception as exc:
        print(f"[App] Error launching Streamlit: {exc}")


if __name__ == "__main__":
    main()