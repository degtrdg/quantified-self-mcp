#!/usr/bin/env python3
"""
Seed database with workout and food data from CSV files
"""
import csv
import os
import psycopg2
from datetime import datetime
from pathlib import Path
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

def seed_workouts(conn):
    """Load workout data from CSV"""
    csv_path = Path(__file__).parent / "workouts.csv"
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        cursor = conn.cursor()
        
        for row in reader:
            # Convert date format
            date = datetime.strptime(row['date'], '%Y-%m-%d').date()
            
            cursor.execute("""
                INSERT INTO workouts (id, exercise, date, sets, reps, weight, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (id) DO NOTHING
            """, (
                row['id'],
                row['exercise'],
                date,
                int(row['sets']),
                int(row['reps']),
                float(row['weight'])
            ))
        
        conn.commit()
        cursor.close()
        print(f"✅ Loaded workout data from {csv_path}")

def seed_food(conn):
    """Load food data from CSV"""
    csv_path = Path(__file__).parent / "food.csv"
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        cursor = conn.cursor()
        
        for row in reader:
            # Convert date format
            date = datetime.strptime(row['date'], '%Y-%m-%d').date()
            
            cursor.execute("""
                INSERT INTO food (id, dish_name, meal_type, estimated_calories, protein_grams, carbs_grams, fat_grams, date, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (id) DO NOTHING
            """, (
                row['id'],
                row['dish_name'],
                row['meal_type'] if row['meal_type'] else None,
                int(row['calories']),
                float(row['protein']),
                float(row['carbs']),
                float(row['fats']),
                date
            ))
        
        conn.commit()
        cursor.close()
        print(f"✅ Loaded food data from {csv_path}")

def main():
    """Main seeding function"""
    try:
        conn = get_db_connection()
        print("🔌 Connected to database")
        
        # Seed both tables
        seed_workouts(conn)
        seed_food(conn)
        
        conn.close()
        print("🌱 Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise

if __name__ == "__main__":
    main()