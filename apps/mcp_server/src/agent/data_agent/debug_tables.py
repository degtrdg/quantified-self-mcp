"""Debug script to see what tables exist"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from database_helpers import db_helper

def debug_tables():
    """Debug what tables exist"""
    print("🔍 Debugging table structure...")
    
    # Check what tables exist
    print("\n1. All tables in public schema:")
    try:
        tables = db_helper.execute_query("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        for table in tables:
            print(f"  - {table['table_name']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Check if table_metadata exists
    print("\n2. Check table_metadata structure:")
    try:
        columns = db_helper.execute_query("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'table_metadata' AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        if columns:
            print("  table_metadata columns:")
            for col in columns:
                print(f"    - {col['column_name']}: {col['data_type']}")
        else:
            print("  ❌ table_metadata not found")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Check if there's any data in table_metadata
    print("\n3. table_metadata content:")
    try:
        data = db_helper.execute_query("SELECT * FROM table_metadata LIMIT 3")
        if data:
            print(f"  Found {len(data)} rows")
            for row in data:
                print(f"    - {row}")
        else:
            print("  No data in table_metadata")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_tables()