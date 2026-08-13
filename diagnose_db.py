"""
Diagnostic script to verify database state and product persistence.
Checks:
1. Database file exists and is accessible
2. Schema is correctly created
3. Products are actually in database
4. Shows sample data
"""

import os
import sqlite3
from datetime import datetime
from database.db_manager import SessionLocal, ProductListing, init_db

print("="*70)
print("RETAIL INTEL PLATFORM - DATABASE DIAGNOSTIC")
print("="*70)

# 1. Check database file
db_path = "database/db.sqlite"
print(f"\n[1] DATABASE FILE CHECK")
print(f"  Path: {db_path}")
if os.path.exists(db_path):
    file_size = os.path.getsize(db_path)
    print(f"  ✓ File exists: YES ({file_size:,} bytes)")
else:
    print(f"  ✗ File exists: NO")

# 2. Initialize database
print(f"\n[2] DATABASE INITIALIZATION")
try:
    init_db()
    print(f"  ✓ Database schema initialized")
except Exception as e:
    print(f"  ✗ Error: {e}")

# 3. Check schema
print(f"\n[3] DATABASE SCHEMA")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"  Tables found: {len(tables)}")
    for table in tables:
        print(f"    - {table[0]}")
    
    # Get product_listings columns
    cursor.execute("PRAGMA table_info(product_listings)")
    columns = cursor.fetchall()
    print(f"\n  product_listings columns ({len(columns)}):")
    for col in columns:
        col_id, col_name, col_type, _, _, _ = col
        print(f"    - {col_name}: {col_type}")
    
    conn.close()
except Exception as e:
    print(f"  ✗ Error: {e}")

# 4. Count products via SQLAlchemy ORM
print(f"\n[4] PRODUCTS IN DATABASE (ORM Query)")
try:
    session = SessionLocal()
    total_products = session.query(ProductListing).count()
    print(f"  Total products: {total_products}")
    
    if total_products > 0:
        # Show by brand
        print(f"\n  Products by Brand:")
        brands = session.query(ProductListing.brand, 
                              ProductListing).group_by(ProductListing.brand).all()
        
        from sqlalchemy import func
        brand_counts = session.query(
            ProductListing.brand, 
            func.count(ProductListing.id).label('count')
        ).group_by(ProductListing.brand).all()
        
        for brand, count in brand_counts:
            print(f"    - {brand}: {count}")
        
        # Show by platform
        print(f"\n  Products by Platform:")
        platform_counts = session.query(
            ProductListing.platform, 
            func.count(ProductListing.id).label('count')
        ).group_by(ProductListing.platform).all()
        
        for platform, count in platform_counts:
            print(f"    - {platform}: {count}")
        
        # Show sample products
        print(f"\n  Sample Products (first 5):")
        samples = session.query(ProductListing).limit(5).all()
        for i, p in enumerate(samples, 1):
            print(f"    [{i}] {p.brand} | {p.title[:50]}... | ${p.price} | {p.platform}")
        
        # Check for duplicates by URL
        print(f"\n  Duplicate URL Check:")
        from sqlalchemy import func
        duplicates = session.query(
            ProductListing.url,
            func.count(ProductListing.id).label('count')
        ).filter(ProductListing.url != None).group_by(ProductListing.url).having(
            func.count(ProductListing.id) > 1
        ).all()
        
        if duplicates:
            print(f"    ✗ Found {len(duplicates)} duplicate URLs:")
            for url, count in duplicates[:5]:
                print(f"      - {url}: appears {count} times")
        else:
            print(f"    ✓ No duplicate URLs found")
    
    session.close()
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# 5. Count products via direct SQL
print(f"\n[5] PRODUCTS IN DATABASE (Direct SQL)")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM product_listings")
    count = cursor.fetchone()[0]
    print(f"  Total products: {count}")
    
    cursor.execute("""
        SELECT brand, COUNT(*) as count 
        FROM product_listings 
        GROUP BY brand 
        ORDER BY count DESC
    """)
    brand_data = cursor.fetchall()
    if brand_data:
        print(f"\n  Products by Brand (SQL):")
        for brand, count in brand_data:
            print(f"    - {brand}: {count}")
    
    conn.close()
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n" + "="*70)
print("END DIAGNOSTIC")
print("="*70)
