"""Trace the exact line causing the tuple index error"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from database_helpers import db_helper

def trace_list_tables():
    """Trace exactly where the error occurs"""
    
    print("Step 1: Get basic tables...")
    try:
        basic_query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND table_name NOT LIKE '%_metadata'
        ORDER BY table_name
        """
        basic_tables = db_helper.execute_query(basic_query)
        print(f"  Basic tables: {basic_tables}")
        
        if not basic_tables:
            print("  No tables found")
            return
        
        print("\nStep 2: Process each table...")
        for i, table_row in enumerate(basic_tables):
            print(f"\n  Processing table {i}: {table_row}")
            table_name = table_row['table_name']
            print(f"    table_name: {table_name}")
            
            print("    Getting metadata...")
            metadata_query = """
            SELECT description, purpose
            FROM table_metadata 
            WHERE table_name = %s
            """
            metadata = db_helper.execute_query(metadata_query, (table_name,))
            print(f"    metadata result: {metadata}")
            
            print("    Getting column count...")
            column_query = """
            SELECT COUNT(*) as column_count
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = 'public'
            """
            column_info = db_helper.execute_query(column_query, (table_name,))
            print(f"    column_info result: {column_info}")
            
            print("    Building table_info...")
            
            # This is where the error might be
            desc = metadata[0]['description'] if metadata and len(metadata) > 0 and metadata[0]['description'] else 'No description'
            print(f"    description: {desc}")
            
            purpose = metadata[0]['purpose'] if metadata and len(metadata) > 0 and metadata[0]['purpose'] else 'No purpose defined'
            print(f"    purpose: {purpose}")
            
            count = column_info[0]['column_count'] if column_info and len(column_info) > 0 else 0
            print(f"    count: {count}")
            
            print(f"    ✅ Table {table_name} processed successfully")
            
    except Exception as e:
        import traceback
        print(f"❌ Error: {e}")
        print("Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    trace_list_tables()