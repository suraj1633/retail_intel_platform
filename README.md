# 🛒 Retail Intelligence & Compliance Platform

A comprehensive multi-brand competitive intelligence dashboard tracking pricing, promotions, and compliance metrics across retail platforms in real-time.

## 📋 Overview

This platform provides daily monitoring and benchmarking of leading computing brands (Intel, AMD, Qualcomm, Apple) across retail platforms (Newegg US, Mercado Libre BR). It tracks:

- **Retailer Compliance (S1-P5 Rubric)** — Brand presence, badges, specs, and rich media
- **Pricing & Promotions** — Real-time price tracking with alerts
- **Share of Shelf (SoS)** — Market visibility metrics per brand
- **Share of Voice (Search)** — Search ranking and presence
- **Banner Tracking** — Homepage banner visibility monitoring
- **SKU Explorer** — Full product drill-down with specs
- **AI Insights** — Natural language Q&A chatbot for business queries

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.9+
- **SQLite** (included with Python)
- **Git** (optional, for version control)
- **pip** (Python package manager)

### Installation

#### 1. Clone or navigate to the project

```bash
cd d:\study\retail_intel_platform
```

#### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Mac/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

### Option 1: Run the Streamlit Dashboard (Recommended)

```bash
streamlit run dashboard/app.py
```

The dashboard will open automatically at: **http://localhost:8502**

### Option 2: Run via main.py (Includes seeding)

```bash
python main.py
```

This will:

- Initialize the database
- Seed sample data (302 products)
- Launch the Streamlit dashboard

### Option 3: Run Live Scraper

```bash
python run_scraper.py
```

This fetches live product data from:

- **Newegg US** — Gaming & Creator laptops
- **Mercado Libre BR** — Gaming notebooks & MacBook Air models

---

## 📊 Dashboard Features

### Tab 1: 📋 Retailer Compliance Audits

Evaluates brand presence on listing and product pages against the S1-P5 rubric:

- **S1** — Brand name in listing title
- **S2** — Badge on listing tile
- **P1** — Brand/processor in product page title
- **P2** — Badge on product page
- **P3** — Brand/processor in spec table
- **P4** — Brand-led rich media
- **P5** — OEM rich media

**Weighting:** 85% Notebook / 15% Desktop

### Tab 2: 🖼️ Banner & Real Estate Tracking

Monitors homepage banner visibility and brand exposure across platforms.

### Tab 3: 📊 Share of Voice (SoV)

Tracks search presence and ranking for each brand per platform and keyword.

### Tab 4: 🔍 SKU Explorer

Search and drill down into individual products with full specs, pricing, and compliance details.

### Tab 5: 🤖 AI Insights Chatbot

Ask natural language questions:

- "Which brand is winning on price?"
- "Which platform has the most Intel products?"
- "What's the average price by brand?"

---

## 📁 Project Structure

```
retail_intel_platform/
├── dashboard/                          # Streamlit UI
│   ├── app.py                         # Main dashboard entry
│   ├── export_utils.py                # CSV export utilities
│   └── components/
│       ├── audit_tab.py               # S1-P5 compliance view
│       ├── banner_tab.py              # Banner tracking
│       ├── chatbot.py                 # AI insights
│       ├── sku_explorer.py            # Product drill-down
│       └── sos_tab.py                 # Share of Voice
│
├── engine/                            # Business logic
│   ├── audit_scorer.py                # S1-P5 scoring logic
│   ├── analytics.py                   # Share of Voice calculations
│   ├── alert_engine.py                # Price/compliance alerts
│   ├── brand_parser.py                # Brand & product extraction
│   └── data_pipeline.py               # Data seeding & scraping
│
├── database/                          # Data persistence
│   ├── db_manager.py                  # SQLAlchemy models
│   └── db.sqlite                      # SQLite database (auto-created)
│
├── scrapers/                          # Platform-specific scrapers
│   ├── newegg_scraper.py              # Newegg US extraction
│   ├── mercadolibre_scraper.py        # Mercado Libre BR extraction
│   ├── banner_scraper.py              # Homepage banner detection
│   └── stealth_driver.py              # HTTP client with rotation
│
├── config/                            # Settings
│   ├── settings.py                    # Platform & brand definitions
│   └── audit_rules.py                 # Weighting config
│
├── tests/                             # Test suite
│   ├── test_audit_scorer.py           # Scoring logic tests
│   └── test_brand_parser.py           # Brand parsing tests
│
├── main.py                            # Dashboard launcher
├── run_scraper.py                     # Scraper entry point
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

---

## ⚙️ Configuration

### Tracked Brands

Edit `config/settings.py` to modify:

```python
DEFAULT_BRANDS = ["Intel", "AMD", "Qualcomm", "Apple"]
```

### Tracked Platforms

```python
DEFAULT_PLATFORM_MAP = {
    "Newegg US": "newegg",
    "Mercado Libre BR": "mercadolibre",
}
```

### Product Types & Exclusions

Edit `engine/brand_parser.py`:

- **Included:** Desktops, Notebooks, Workstations, Tablets, CPU/GPU components
- **Excluded:** Monitors, keyboards, mice, cameras, gift cards

### Audit Scoring Weights

```python
DEFAULT_AUDIT_WEIGHTS = {
    "Notebook": 0.85,
    "Desktop": 0.15,
}
```

---

## 🧪 Running Tests

Run the full test suite:

```bash
pytest tests/ -q
```

Run specific tests:

```bash
pytest tests/test_audit_scorer.py -v
pytest tests/test_brand_parser.py -v
```

**Expected:** 12 tests passing

---

## 📦 Dependencies

Key libraries:

- **streamlit** — Dashboard UI
- **pandas** — Data manipulation
- **sqlalchemy** — ORM & database
- **plotly** — Interactive charts
- **beautifulsoup4** — Web scraping
- **curl-cffi** — HTTP client with anti-bot bypass
- **pytest** — Testing framework

See `requirements.txt` for full list.

---

## 🔍 Data Flow

```
Scrapers (Newegg, Mercado Libre)
    ↓
Brand Parser (Extract brand, OEM, badges)
    ↓
Validation (Filter zero-price, accessories, invalid rows)
    ↓
SQLite Database (ProductListing, BannerRecord, AuditRecord)
    ↓
Dashboard Components (Tabs, filters, analytics)
    ↓
User View (Compliance scores, pricing trends, alerts)
```

---

## 🚨 Troubleshooting

### Dashboard Won't Start

```bash
# Check if port 8502 is in use
netstat -ano | findstr :8502

# Or specify a different port
streamlit run dashboard/app.py --server.port=8503
```

### Database Not Found

```bash
# Reinitialize the database
rm database/db.sqlite
python main.py
```

### Scraper Returns Empty Results

The scrapers use fallback data generation when live scraping fails. To debug:

```bash
python run_scraper.py  # Check console output for errors
```

### Import Errors

```bash
# Ensure virtual environment is activated
pip install -r requirements.txt --upgrade
```

---

## 📊 Key Metrics

### Compliance Score (S1-P5)

- **Raw Score** — % of passed checks (100% = all pass, 0% = all fail)
- **Weighted Score** — Adjusted for product type (Notebooks weighted 85%)
- **Pass Rate** — % of checks passed across all products per brand

### Share of Voice

- **Search Appearances** — # of top rankings per brand per keyword
- **SoV %** — (Appearances / Total) × 100

### Price Metrics

- **Average Price** — Mean price per brand
- **Price Index** — Relative pricing vs. platform average
- **Discounts** — Promo/MSRP variance

---

## 📝 API & Data Access

### Get Raw Data

```python
from database.db_manager import SessionLocal, ProductListing
session = SessionLocal()
products = session.query(ProductListing).filter_by(brand="Intel").all()
```

### Export Reports

- Use the "Download Audit CSV" button in the dashboard
- Or programmatically via `dashboard/export_utils.py`

---

## 🎯 Common Use Cases

### Run Daily Pipeline

```bash
# Schedule with Windows Task Scheduler or cron
python run_scraper.py
```

### Check Compliance by Brand

1. Open dashboard → **Retailer Compliance Audits**
2. Filter by Brand in sidebar
3. Review S1-P5 heatmap and pass rates

### Find Price Drops

1. Check **Alert Engine** output in console during scrape
2. Or query: `python -c "from engine.alert_engine import check_price_drops; check_price_drops()"`

### Compare Brands Across Platforms

1. **Share of Voice** tab → Select platform & brands
2. **SKU Explorer** tab → Compare specs & prices side-by-side

---

## 📞 Support

For issues or questions:

1. Check console output for error messages
2. Review test suite: `pytest tests/ -v`
3. Check database integrity: `python -c "from database.db_manager import init_db; init_db(); print('DB OK')"`

---

## 📄 License

Internal project for Bridge AI competitive intelligence platform.

---

## 🔄 Updates

Last updated: 2026-08-13

**Recent fixes:**

- ✅ S1-P5 rubric scoring aligned with project brief
- ✅ Accessory filtering consistent across scrapers
- ✅ Data quality validation for pricing
- ✅ Share of Voice analytics updated
- ✅ Badge detection for all 4 brands (Intel, AMD, Qualcomm, Apple)
