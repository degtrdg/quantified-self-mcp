"""Simple debug to isolate the issue"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from database_helpers import db_helper

def simple_test():
    """Test simple queries step by step"""
    
    print("1. Testing basic table query...")
    try:
        result = db_helper.execute_query("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'workouts'
        """)
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n2. Testing table_metadata query...")
    try:
        result = db_helper.execute_query("""
            SELECT description, purpose FROM table_metadata WHERE table_name = %s
        """, ('workouts',))
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n3. Testing column count query...")
    try:
        result = db_helper.execute_query("""
            SELECT COUNT(*) as column_count FROM information_schema.columns
            WHERE table_name = %s AND table_schema = 'public'
        """, ('workouts',))
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    simple_test()