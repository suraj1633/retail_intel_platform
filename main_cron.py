# main_cron.py
"""
Simple scheduler for 3x daily data pipeline execution.
Uses only built-in libraries (no external dependencies).
Runs at 08:00, 14:00, and 20:00 every day.
"""

from engine.data_pipeline import run_live_pipeline
import logging
import time
import threading
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Scheduled hours for pipeline execution (24-hour format)
SCHEDULED_HOURS = [8, 14, 20]

def scheduled_job():
    """Runs the live pipeline job."""
    try:
        logger.info("=" * 60)
        logger.info("Executing 3x daily automated pipeline...")
        logger.info("=" * 60)
        run_live_pipeline()
        logger.info("Pipeline execution completed successfully.")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"Error during pipeline execution: {e}", exc_info=True)

def scheduler_loop():
    """Main scheduler loop - runs pipeline at scheduled times."""
    logger.info("Scheduler loop started. Monitoring for scheduled execution times...")
    last_run_date = None
    
    while True:
        now = datetime.now()
        current_hour = now.hour
        current_date = now.date()
        
        # Check if current hour matches any scheduled hour and hasn't run today yet
        if current_hour in SCHEDULED_HOURS:
            # Ensure we only run once per day at each scheduled time
            if last_run_date != current_date or current_hour not in SCHEDULED_HOURS:
                logger.info(f"Scheduled time reached: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                scheduled_job()
                last_run_date = current_date
        
        # Sleep for 60 seconds before next check
        time.sleep(60)

if __name__ == "__main__":
    logger.info("Starting Bridge AI Automated 3x Daily Pipeline Scheduler...")
    logger.info(f"Scheduled to run at: {', '.join([f'{h:02d}:00' for h in SCHEDULED_HOURS])} daily")
    logger.info("Press Ctrl+C to stop the scheduler.")
    
    try:
        # Run scheduler in main thread
        scheduler_loop()
    except KeyboardInterrupt:
        logger.info("\nScheduler stopped by user.")
    except Exception as e:
        logger.error(f"Fatal scheduler error: {e}", exc_info=True)