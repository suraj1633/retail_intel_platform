"""
database/db_manager.py
SQLAlchemy schema models and database connection management.
"""

import datetime
import os

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, UniqueConstraint, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite database file configuration
DB_PATH = os.getenv("DB_PATH", "sqlite:///database/db.sqlite")

engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ProductListing(Base):
    __tablename__ = "product_listings"
    __table_args__ = (UniqueConstraint('url', name='uq_product_url'),)

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    price = Column(Float, default=0.0)
    msrp = Column(Float, default=0.0)
    is_promo = Column(Boolean, default=False)
    brand = Column(String, index=True)
    oem = Column(String, index=True, nullable=True)
    product_type = Column(String, default="Notebook")
    platform = Column(String, index=True)
    url = Column(String, unique=True, nullable=True)
    rank = Column(Integer, default=1)
    has_listing_badge = Column(Boolean, default=False)
    has_pdp_badge = Column(Boolean, default=False)
    has_spec_table_mention = Column(Boolean, default=False)
    has_brand_rich_media = Column(Boolean, default=False)
    has_oem_rich_media = Column(Boolean, default=False)
    detected_badges = Column(String, nullable=True)
    source = Column(String, default="SCRAPED")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class AuditRecord(Base):
    __tablename__ = "audit_records"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    platform = Column(String, index=True)
    overall_score = Column(Float, default=0.0)
    s1_p5_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class BannerRecord(Base):
    __tablename__ = "banner_records"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True)
    brand = Column(String, index=True)
    target_url = Column(String)
    screenshot_path = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


def init_db():
    """Creates database tables if they do not exist."""
    os.makedirs("database", exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db_session():
    """Returns a new SQLAlchemy ORM session."""
    return SessionLocal()


def is_valid_product_record(record: dict) -> bool:
    """Reject incomplete or financially invalid product entries before they reach analytics."""
    if not isinstance(record, dict):
        return False

    title = str(record.get("title") or "").strip()
    price = record.get("price")
    brand = str(record.get("brand") or "").strip()

    if not title:
        return False
    if price is None:
        return False
    try:
        numeric_price = float(price)
    except (TypeError, ValueError):
        return False
    if numeric_price <= 0:
        return False
    if not brand:
        return False
    return True