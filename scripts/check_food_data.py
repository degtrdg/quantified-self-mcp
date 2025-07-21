#!/usr/bin/env python3
"""
Check current food data in database for specific date range
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

def check_food_data(conn):
    """Check food data for the critical week"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT date, dish_name, carbs_grams, protein_grams, estimated_calories, feeling_after
        FROM food 
        WHERE date BETWEEN '2025-06-25' AND '2025-07-05'
        ORDER BY date
    """)
    
    results = cursor.fetchall()
    cursor.close()
    
    print("📊 Food data for June 25 - July 5, 2025:")
    print("Date       | Carbs | Protein | Calories | Feeling")
    print("-" * 60)
    
    for date, dish, carbs, protein, calories, feeling in results:
        feeling_str = feeling if feeling else "N/A"
        print(f"{date} | {carbs:5.0f}g | {protein:6.0f}g | {calories:7.0f} | {feeling_str}")

def check_running_data(conn):
    """Check running data for the same period"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT date, exercise, reps, weight, rpe
        FROM workouts 
        WHERE exercise = 'running' AND date BETWEEN '2025-06-20' AND '2025-07-10'
        ORDER BY date
    """)
    
    results = cursor.fetchall()
    cursor.close()
    
    print("\n🏃 Running data for June 20 - July 10, 2025:")
    print("Date       | Duration | RPE | Notes")
    print("-" * 40)
    
    for date, exercise, duration, weight, rpe in results:
        rpe_str = str(rpe) if rpe else "N/A"
        print(f"{date} | {duration:7.0f}min | {rpe_str:3} | Running")

def main():
    """Main function to check data"""
    try:
        conn = get_db_connection()
        print("🔌 Connected to database")
        
        check_food_data(conn)
        check_running_data(conn)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking data: {e}")
        raise

if __name__ == "__main__":
    main()