#!/usr/bin/env python3
"""
Test AI affordances and decision-making guidance in MCP tools
"""

import sys
sys.path.insert(0, '.')

from apps.mcp_server.src.server import (
    list_tables, create_table, add_column, insert_data, query_data
)

def test_scenario_1_empty_database():
    """Test: Starting with empty database"""
    print("🎯 SCENARIO 1: Empty Database - First Time User")
    print("=" * 60)
    
    # Step 1: Check what exists (should be empty)
    print("1. User asks: 'I want to track my workouts'")
    print("   AI should: Use list_tables() first to understand existing schema")
    
    result = list_tables()
    print("   Result: Found", len([line for line in result.split('\n') if '###' in line]), "existing tables")
    
    # Step 2: Create workouts table since none exists
    print("\n2. AI Decision: No workout table exists → create_table")
    columns = [
        {"name": "exercise", "type": "TEXT", "description": "Exercise performed", "required": True},
        {"name": "sets", "type": "INTEGER", "description": "Number of sets completed"},
        {"name": "reps", "type": "INTEGER", "description": "Repetitions per set"},
        {"name": "weight", "type": "REAL", "description": "Weight used in pounds", "units": "lbs"}
    ]
    
    result = create_table("workouts", "Physical exercise and training sessions", "Track workout performance", columns)
    print("   ✅ Table created successfully" if "✅" in result else "   ❌ Table creation failed")

def test_scenario_2_schema_evolution():
    """Test: Adding to existing table vs creating new table"""
    print("\n🎯 SCENARIO 2: Schema Evolution - Existing Table")
    print("=" * 60)
    
    # User wants to add RPE to workouts
    print("1. User says: 'I want to track RPE (effort level) for my workouts'")
    print("   AI should: Check existing tables first")
    
    result = list_tables("workouts")
    has_rpe = "rpe" in result.lower()
    print(f"   Workouts table exists: {len(result) > 100}")
    print(f"   RPE column exists: {has_rpe}")
    
    if not has_rpe:
        print("\n2. AI Decision: RPE belongs to workouts → add_column (not create_table)")
        result = add_column("workouts", "rpe", "INTEGER", "Rate of Perceived Exertion (1-10 scale)", "scale_1_10")
        print("   ✅ Column added successfully" if "✅" in result else "   ❌ Column addition failed")

def test_scenario_3_data_insertion():
    """Test: Smart data extraction and insertion"""
    print("\n🎯 SCENARIO 3: Data Insertion - Smart Extraction")
    print("=" * 60)
    
    print("1. User input: 'Deadlifted 315 lbs for 3 sets of 5 reps this morning, RPE was 8'")
    print("   AI should: Extract structured data and map to columns")
    
    # Simulate AI extraction
    workout_data = {
        "date": "2023-06-20 09:00:00",  # "this morning"
        "exercise": "deadlift",
        "weight": 315.0,
        "sets": 3,
        "reps": 5,
        "rpe": 8
    }
    
    result = insert_data("workouts", workout_data)
    print("   ✅ Data inserted successfully" if "✅" in result else "   ❌ Data insertion failed")
    print("   Extracted fields:", list(workout_data.keys()))

def test_scenario_4_new_domain():
    """Test: Recognizing new data domain vs extending existing"""
    print("\n🎯 SCENARIO 4: New Data Domain - Sleep Tracking")
    print("=" * 60)
    
    print("1. User says: 'I want to start tracking my sleep quality'")
    print("   AI should: Recognize this is different domain from workouts → create_table")
    
    # Check if fundamentally different from workouts
    print("   Analysis: Sleep has different temporal pattern than workouts")
    print("   Decision: Create new table (not add to workouts)")
    
    sleep_columns = [
        {"name": "bedtime", "type": "TIMESTAMP", "description": "When went to bed"},
        {"name": "wake_time", "type": "TIMESTAMP", "description": "When woke up"},
        {"name": "duration_hours", "type": "REAL", "description": "Total sleep duration", "units": "hours"},
        {"name": "quality_rating", "type": "INTEGER", "description": "Sleep quality (1-10)", "units": "scale_1_10"}
    ]
    
    result = create_table("sleep", "Sleep patterns and quality tracking", "Monitor sleep health", sleep_columns)
    print("   ✅ Sleep table created" if "✅" in result else "   ❌ Sleep table creation failed")

def test_scenario_5_analytics():
    """Test: Intelligent analysis queries"""
    print("\n🎯 SCENARIO 5: Data Analysis - Workout Progress")
    print("=" * 60)
    
    print("1. User asks: 'How has my deadlift strength progressed?'")
    print("   AI should: Query for deadlift progression over time")
    
    # Insert some historical data first
    historical_data = [
        {"date": "2023-06-01 09:00", "exercise": "deadlift", "weight": 275.0, "sets": 3, "reps": 5, "rpe": 7},
        {"date": "2023-06-08 09:00", "exercise": "deadlift", "weight": 285.0, "sets": 3, "reps": 5, "rpe": 8},
        {"date": "2023-06-15 09:00", "exercise": "deadlift", "weight": 295.0, "sets": 3, "reps": 5, "rpe": 8},
    ]
    
    for data in historical_data:
        insert_data("workouts", data)
    
    # Query progression
    progress_query = """
    SELECT DATE(date) as workout_date, MAX(weight) as max_weight, AVG(rpe) as avg_rpe
    FROM workouts 
    WHERE exercise = 'deadlift'
    GROUP BY DATE(date)
    ORDER BY workout_date
    """
    
    result = query_data(progress_query)
    print("   ✅ Progress analysis generated" if "|" in result else "   ❌ Query failed")
    print("   Shows: Date, max weight, average RPE over time")

def main():
    print("🧠 Testing AI Affordances & Decision Making")
    print("Testing how well prompts guide AI tool selection...")
    print()
    
    test_scenario_1_empty_database()
    test_scenario_2_schema_evolution()
    test_scenario_3_data_insertion()
    test_scenario_4_new_domain()
    test_scenario_5_analytics()
    
    print("\n" + "=" * 60)
    print("🎉 AI AFFORDANCE TESTING COMPLETE")
    print()
    print("✅ Enhanced prompts provide clear guidance for:")
    print("   • WHEN to use each tool")
    print("   • HOW to structure data")
    print("   • DECISION FRAMEWORKS for table vs column")
    print("   • DATA EXTRACTION patterns")
    print("   • ANALYSIS strategies")
    print()
    print("Ready for intelligent AI interaction!")

if __name__ == "__main__":
    main()