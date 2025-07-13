#!/usr/bin/env python3
"""
Check database schema for existing tables
"""
import os
import psycopg2
from dotenv import load_dotenv

def get_db_connection():
    """Get database connection using environment variables"""
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise EnvironmentError(
            "DATABASE_URL environment variable is required. "
            "Please set it in your .env file with your PostgreSQL connection string."
        )
    
    return psycopg2.connect(database_url)

def check_table_schema(conn, table_name):
    """Check schema for a specific table"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    
    columns = cursor.fetchall()
    cursor.close()
    
    if columns:
        print(f"\n📋 {table_name} table schema:")
        for col_name, data_type, nullable, default in columns:
            print(f"  - {col_name}: {data_type} {'(nullable)' if nullable == 'YES' else ''} {f'default: {default}' if default else ''}")
    else:
        print(f"\n❌ Table '{table_name}' does not exist")

def main():
    """Main function to check schemas"""
    try:
        conn = get_db_connection()
        print("🔌 Connected to database")
        
        # Check both tables
        check_table_schema(conn, 'workouts')
        check_table_schema(conn, 'food')
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking schema: {e}")
        raise

if __name__ == "__main__":
    main()