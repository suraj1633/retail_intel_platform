# main_cron.py
from apscheduler.schedulers.blocking import BlockingScheduler
from engine.data_pipeline import run_live_pipeline
import datetime

def scheduled_job():
    print(f"[{datetime.datetime.now()}] Executing 3x daily automated pipeline...")
    run_live_pipeline()

scheduler = BlockingScheduler()

# Run at 08:00, 14:00, and 20:00 every day
scheduler.add_job(scheduled_job, 'cron', hour='8,14,20')

if __name__ == "__main__":
    print("Starting Bridge AI Automated 3x Daily Pipeline Scheduler...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass