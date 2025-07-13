#!/usr/bin/env python3
"""Seed database with demo CSV data for quantified self demo"""

import csv
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the path so we can import the database module
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "apps" / "mcp_server" / "src"))

from database import db
from tools.table_metadata import store_metadata

# Load environment variables
load_dotenv(project_root / ".env")

async def create_tables_with_metadata():
    """Create all demo tables with their metadata"""
    
    # Create workouts table
    workouts_sql = """
    CREATE TABLE IF NOT EXISTS workouts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        exercise TEXT NOT NULL,
        date TIMESTAMP NOT NULL,
        sets INTEGER,
        reps INTEGER,
        weight REAL,
        duration_minutes INTEGER,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    await db.execute_query(workouts_sql)
    await store_metadata(
        table_name="workouts",
        description="Exercise and strength training sessions",
        purpose="Track workout progress, strength gains, and exercise patterns",
        ai_learnings={
            "common_exercises": ["deadlift", "bench_press", "squat", "overhead_press"],
            "weight_units": "lbs",
            "typical_rep_ranges": "3-10 reps per set",
            "data_patterns": "Users often track compound movements most consistently"
        }
    )
    
    # Create food table
    food_sql = """
    CREATE TABLE IF NOT EXISTS food (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        dish_name TEXT NOT NULL,
        date TIMESTAMP NOT NULL,
        protein REAL,
        carbs REAL,
        fats REAL,
        fiber REAL,
        calories INTEGER,
        liked BOOLEAN,
        meal_type TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    await db.execute_query(food_sql)
    await store_metadata(
        table_name="food",
        description="Nutritional intake and meal tracking",
        purpose="Monitor nutrition balance, food preferences, and eating patterns",
        ai_learnings={
            "macro_nutrients": ["protein", "carbs", "fats", "fiber"],
            "meal_types": ["breakfast", "lunch", "dinner", "snack"],
            "preference_tracking": "Boolean 'liked' field helps identify food preferences",
            "portion_estimation": "Users often estimate macros, exact precision not expected"
        }
    )
    
    # Create sleep table
    sleep_sql = """
    CREATE TABLE IF NOT EXISTS sleep (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        bedtime TIMESTAMP,
        wake_time TIMESTAMP,
        date DATE NOT NULL,
        duration_hours REAL,
        quality_rating INTEGER,
        dream_recall BOOLEAN,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    await db.execute_query(sleep_sql)
    await store_metadata(
        table_name="sleep",
        description="Sleep patterns and quality tracking",
        purpose="Analyze sleep quality, duration patterns, and correlation with other metrics",
        ai_learnings={
            "quality_scale": "1-10 rating where 10 is excellent sleep",
            "optimal_duration": "7.5-8.5 hours seems optimal for this user",
            "dream_tracking": "Binary tracking of dream recall as sleep quality indicator",
            "bedtime_patterns": "Earlier bedtimes correlate with better quality ratings"
        }
    )
    
    # Create mood table
    mood_sql = """
    CREATE TABLE IF NOT EXISTS mood (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        date TIMESTAMP NOT NULL,
        mood_rating INTEGER,
        energy_level INTEGER,
        stress_level INTEGER,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    await db.execute_query(mood_sql)
    await store_metadata(
        table_name="mood",
        description="Emotional state and energy level tracking",
        purpose="Track mood patterns, energy cycles, and stress levels for wellbeing insights",
        ai_learnings={
            "rating_scales": "All ratings on 1-10 scale (mood, energy, stress)",
            "stress_inverse": "Lower stress_level numbers indicate less stress",
            "daily_variation": "Mood and energy often vary throughout the day",
            "correlation_potential": "Strong correlation candidates with sleep and exercise"
        }
    )


async def load_csv_data(table_name: str, csv_file: Path):
    """Load data from CSV file into specified table"""
    print(f"Loading {csv_file.name} into {table_name} table...")
    
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        rows_inserted = 0
        
        for row in reader:
            # Remove id and created_at if present (let database handle these)
            if 'id' in row:
                del row['id']
            if 'created_at' in row:
                del row['created_at']
            
            # Convert empty strings to None
            for key, value in row.items():
                if value == '':
                    row[key] = None
                elif key in ['liked', 'dream_recall'] and value:
                    # Convert boolean strings
                    row[key] = value.lower() in ['true', '1', 'yes']
                elif key in ['sets', 'reps', 'duration_minutes', 'calories', 'quality_rating', 
                           'mood_rating', 'energy_level', 'stress_level'] and value:
                    # Convert integer fields
                    row[key] = int(value)
                elif key in ['weight', 'protein', 'carbs', 'fats', 'fiber', 'duration_hours'] and value:
                    # Convert float fields
                    row[key] = float(value)
            
            # Build INSERT query
            columns = list(row.keys())
            placeholders = ', '.join(['$' + str(i+1) for i in range(len(columns))])
            values = list(row.values())
            
            insert_sql = f"""
            INSERT INTO {table_name} ({', '.join(columns)}) 
            VALUES ({placeholders})
            """
            
            success = await db.execute_query(insert_sql, *values)
            if success:
                rows_inserted += 1
            else:
                print(f"Failed to insert row: {row}")
        
        print(f"Successfully inserted {rows_inserted} rows into {table_name}")


async def main():
    """Main seeding function"""
    print("🌱 Starting database seeding with demo data...")
    
    # Connect to database
    if not db.connect():
        print("❌ Failed to connect to database")
        return
    
    print("✅ Connected to database")
    
    # Create tables and metadata
    await create_tables_with_metadata()
    print("✅ Created tables with metadata")
    
    # Load CSV data
    data_dir = project_root / "data"
    csv_files = [
        ("workouts", "workouts_demo.csv"),
        ("food", "food_demo.csv"),
        ("sleep", "sleep_demo.csv"),
        ("mood", "mood_demo.csv")
    ]
    
    for table_name, csv_filename in csv_files:
        csv_path = data_dir / csv_filename
        if csv_path.exists():
            await load_csv_data(table_name, csv_path)
        else:
            print(f"⚠️  CSV file not found: {csv_path}")
    
    # Close database connection
    db.close()
    print("🎉 Demo data seeding completed!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())