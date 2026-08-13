# run.ps1
if (-not (Test-Path "venv")) {
    Write-Host "Creating Virtual Environment..."
    python -m venv venv
}

Write-Host "Activating Virtual Environment & Installing Dependencies..."
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium

if (-not (Test-Path "database\db.sqlite")) {
    Write-Host "Initializing Database..."
    python -c "from database.db_manager import init_db; init_db()"
}

Write-Host "Launching Retail Intelligence Dashboard..."
streamlit run dashboard/app.py