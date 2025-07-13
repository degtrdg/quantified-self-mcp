#!/usr/bin/env python3
"""
Export database tables to CSV files for analysis
"""

import os
import csv
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def export_table_to_csv(table_name: str, output_dir: str = "data/export"):
    """Export a database table to CSV file"""
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Connect to database
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise EnvironmentError("DATABASE_URL not found in environment variables")
    
    try:
        with psycopg2.connect(database_url, cursor_factory=RealDictCursor) as conn:
            with conn.cursor() as cursor:
                # Get all data from table
                cursor.execute(f"SELECT * FROM {table_name} ORDER BY created_at")
                rows = cursor.fetchall()
                
                if not rows:
                    print(f"⚠️  Table '{table_name}' is empty - skipping")
                    return
                
                # Write to CSV
                csv_file = os.path.join(output_dir, f"{table_name}.csv")
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
                
                print(f"✅ Exported {len(rows)} rows from '{table_name}' to {csv_file}")
                
    except Exception as e:
        print(f"❌ Error exporting {table_name}: {e}")

def export_all_tables():
    """Export all data tables to CSV files"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise EnvironmentError("DATABASE_URL not found in environment variables")
    
    try:
        with psycopg2.connect(database_url, cursor_factory=RealDictCursor) as conn:
            with conn.cursor() as cursor:
                # Get list of tables
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                    AND table_name NOT LIKE '%_metadata'
                    ORDER BY table_name
                """)
                
                tables = cursor.fetchall()
                
                if not tables:
                    print("❌ No tables found to export")
                    return
                
                print(f"🔄 Found {len(tables)} tables to export:")
                for table in tables:
                    print(f"   - {table['table_name']}")
                
                print("\n📦 Exporting tables...")
                
                for table in tables:
                    export_table_to_csv(table['table_name'])
                
                print(f"\n🎉 Export complete! Files saved to data/export/")
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")

if __name__ == "__main__":
    export_all_tables()