"""Quantified Self MCP Server - Dynamic table creation for quantified self tracking"""
import asyncio
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .database import db
from .tools.list_tables import handle_list_tables
from .tools.create_table import handle_create_table
from .tools.add_column import handle_add_column
from .tools.insert_data import handle_insert_data
from .tools.query_data import handle_query_data

# Load environment variables
load_dotenv()

# Create FastMCP instance
mcp = FastMCP("Quantified Self MCP")

@mcp.tool()
def list_tables(table_name: Optional[str] = None) -> str:
    """
    DISCOVERY TOOL: Understand what data is already being tracked
    
    Use this FIRST before any other operation to understand the existing schema.
    
    WITHOUT table_name: Get overview of all tables and their purposes
    WITH table_name: Get detailed schema with column descriptions and recent data
    
    DECISION GUIDANCE:
    - Always use this before creating tables or inserting data
    - Use with specific table_name when you need to understand column structure
    - Helps decide whether to create new table vs extend existing one
    """
    return asyncio.run(handle_list_tables({"table_name": table_name}))

@mcp.tool()
def create_table(
    table_name: str,
    description: str,
    purpose: str = "",
    columns: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    SCHEMA CREATION: Create new table for entirely new data types
    
    WHEN TO USE:
    - User wants to track something completely different from existing tables
    - No existing table can logically accommodate the new data
    - The data represents a distinct domain (workouts vs food vs sleep)
    
    WHEN NOT TO USE:
    - Data could fit in existing table with new columns → use add_column instead
    - Just adding new fields to existing concept → use add_column instead
    
    REQUIRED FIELDS (auto-added):
    - id: UUID primary key
    - date: TIMESTAMP when event occurred  
    - created_at: TIMESTAMP when record was created
    
    COLUMN FORMAT:
    columns = [
        {"name": "exercise", "type": "TEXT", "description": "Exercise performed", "required": True},
        {"name": "weight", "type": "REAL", "description": "Weight in pounds", "units": "lbs"}
    ]
    
    EXAMPLES:
    - Create 'workouts' table for tracking exercises
    - Create 'mood' table for emotional tracking  
    - Create 'expenses' table for financial data
    """
    if columns is None:
        columns = []
    args = {
        "table_name": table_name,
        "description": description,
        "purpose": purpose,
        "columns": columns
    }
    return asyncio.run(handle_create_table(args))

@mcp.tool()
def add_column(
    table_name: str,
    column_name: str,
    data_type: str,
    description: str,
    units: Optional[str] = None,
    default_value: Optional[str] = None
) -> str:
    """
    SCHEMA EVOLUTION: Extend existing table with new fields
    
    WHEN TO USE:
    - User mentions new metric for existing data type
    - Need to track additional property of same concept
    - Example: "I want to track RPE for workouts" → add RPE column to workouts table
    
    PREFER THIS OVER create_table when:
    - Data logically belongs with existing table
    - It's an attribute of something already tracked
    - User says "I also want to track..." about existing domain
    
    DATA TYPES:
    - TEXT: Names, descriptions, categories
    - INTEGER: Counts, ratings (1-10), whole numbers  
    - REAL: Measurements, weights, percentages
    - BOOLEAN: Yes/no, true/false values
    - TIMESTAMP: Specific times/dates
    
    EXAMPLES:
    - Add 'rpe' INTEGER column to workouts (rate of perceived exertion)
    - Add 'location' TEXT column to workouts (gym name)
    - Add 'mood_before' INTEGER column to workouts (pre-workout mood)
    """
    args = {
        "table_name": table_name,
        "column_name": column_name,
        "data_type": data_type,
        "description": description,
        "units": units,
        "default_value": default_value
    }
    return asyncio.run(handle_add_column(args))

@mcp.tool()
def insert_data(table_name: str, data: Dict[str, Any]) -> str:
    """
    DATA STORAGE: Store extracted quantified self data
    
    WORKFLOW:
    1. Extract structured data from user input (photo/text)
    2. Map to appropriate table columns  
    3. Insert with automatic timestamps
    
    AUTO-HANDLED FIELDS:
    - id: Generated automatically
    - created_at: Set to current timestamp
    
    REQUIRED FIELD:
    - date: When the event actually occurred (not when recorded)
    
    DATA MAPPING EXAMPLES:
    workouts: {"date": "2023-06-15 10:30", "exercise": "deadlift", "sets": 3, "reps": 5, "weight": 225}
    food: {"date": "2023-06-15 12:30", "dish_name": "chicken salad", "protein": 35, "carbs": 15}
    mood: {"date": "2023-06-15 09:00", "mood_rating": 8, "energy_level": 7, "stress_level": 3}
    
    MISSING COLUMNS:
    If you need a column that doesn't exist, use add_column FIRST, then insert
    """
    args = {
        "table_name": table_name,
        "data": data
    }
    return asyncio.run(handle_insert_data(args))

@mcp.tool()
def query_data(sql: str, result_format: str = "table") -> str:
    """
    DATA ANALYSIS: Query and analyze quantified self patterns
    
    ANALYSIS PATTERNS:
    - Trends over time: GROUP BY date, DATE_TRUNC, time windows
    - Correlations: JOIN tables on matching dates
    - Aggregations: AVG, MAX, MIN, COUNT for insights
    - Filtering: WHERE clauses for specific time periods or conditions
    
    COMMON QUERIES:
    Workout Progress:
    SELECT exercise, MAX(weight) as max_weight, AVG(reps) as avg_reps 
    FROM workouts WHERE exercise = 'deadlift' GROUP BY exercise
    
    Sleep vs Mood Correlation:
    SELECT s.duration_hours, AVG(m.mood_rating) as avg_mood
    FROM sleep s JOIN mood m ON DATE(s.date) = DATE(m.date)
    GROUP BY s.duration_hours ORDER BY s.duration_hours
    
    FORMAT OPTIONS:
    - "table": Markdown table (default, best for structured data)
    - "json": Raw JSON (for programmatic use)
    - "summary": Key statistics with sample rows
    
    SAFETY: Only SELECT queries allowed (no modifications)
    """
    args = {
        "sql": sql,
        "format": result_format
    }
    return asyncio.run(handle_query_data(args))

def main():
    """Main entry point"""
    # Initialize database connection
    if not db.connect():
        print("Failed to connect to database")
        return

    print("Quantified Self MCP Server starting...")
    print("Database connected successfully")

    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()