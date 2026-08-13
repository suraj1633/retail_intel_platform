"""
run_scraper.py
Manual Data Refresh Script.
Executes web scrapers and updates all compliance, shelf share, and banner analytics.
"""

from engine.data_pipeline import run_live_pipeline

if __name__ == "__main__":
    print("==================================================")
    print("      RETAIL INTEL PLATFORM - LIVE SCRAPER       ")
    print("==================================================")
    
    run_live_pipeline()
    
    print("\n[Success] Scraper completed! You can now run 'python main.py' to view the updated dashboard.")