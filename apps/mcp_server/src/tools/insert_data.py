from mcp import Tool
from ..database import db
from .table_metadata import update_ai_learning
import json

INSERT_DATA_TOOL = Tool(
    name="insert_data",
    description="Insert row into table with auto-timestamp",
    inputSchema={
        "type": "object",
        "properties": {
            "table_name": {
                "type": "string",
                "description": "Name of the table to insert into"
            },
            "data": {
                "type": "object",
                "description": "Key-value pairs of column names and values"
            }
        },
        "required": ["table_name", "data"]
    }
)

async def handle_insert_data(arguments: dict) -> str:
    """
    Handle insert_data tool execution
    
    AI DATA EXTRACTION & MAPPING GUIDANCE:
    
    REQUIRED WORKFLOW:
    1. Extract all relevant data from user input
    2. Map to existing table columns  
    3. Handle missing columns (add_column first)
    4. Insert with proper data types
    
    CRITICAL: 'date' FIELD MAPPING:
    - Parse WHEN the event actually occurred
    - Default to current time if not specified
    - Format: 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD HH:MM'
    - Examples: '2023-06-15 10:30:00', '2023-06-15 14:00'
    
    DATA TYPE CONVERSION:
    - Numbers: Convert "225 lbs" → 225.0 (REAL) or 225 (INTEGER)
    - Booleans: "yes"/"good"/"true" → True, "no"/"bad"/"false" → False
    - Text: Keep original for names, notes, categories
    - Scale ratings: "8 out of 10" → 8
    
    SMART EXTRACTION EXAMPLES:
    "Deadlifted 225 for 3 sets of 5 this morning"
    → {"date": "2023-06-15 09:00", "exercise": "deadlift", "weight": 225.0, "sets": 3, "reps": 5}
    
    "Had chicken salad for lunch, about 35g protein"  
    → {"date": "2023-06-15 12:30", "dish_name": "chicken salad", "protein": 35.0}
    
    MISSING COLUMN HANDLING:
    If user mentions data not in existing columns, use add_column FIRST:
    "RPE was 8" + no rpe column → add_column then insert
    """
    try:
        table_name = arguments['table_name']
        data = arguments['data']
        
        # Check if table exists
        table_check = db.execute_query(
            "SELECT table_name FROM information_schema.tables WHERE table_name = %s",
            (table_name,)
        )
        if not table_check:
            return f"❌ Table '{table_name}' does not exist"
        
        # Get table columns to validate data
        columns_info = db.execute_query(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s",
            (table_name,)
        )
        valid_columns = {col['column_name']: col['data_type'] for col in columns_info}
        
        # Filter data to only include valid columns (excluding auto-generated ones)
        filtered_data = {}
        for key, value in data.items():
            if key in valid_columns and key not in ['id', 'created_at']:
                filtered_data[key] = value
            elif key not in valid_columns:
                return f"❌ Column '{key}' does not exist in table '{table_name}'"
        
        if not filtered_data:
            return f"❌ No valid data provided for table '{table_name}'"
        
        # Build INSERT statement
        columns = list(filtered_data.keys())
        placeholders = ', '.join(['%s'] * len(columns))
        values = list(filtered_data.values())
        
        insert_sql = f"""
        INSERT INTO {table_name} ({', '.join(columns)}) 
        VALUES ({placeholders})
        RETURNING id
        """
        
        # Execute insert
        result = db.execute_query(insert_sql, values)
        if not result:
            return f"❌ Error inserting data into table '{table_name}'"
        
        new_id = result[0]['id'] if result else None
        
        # Update AI learnings with insertion patterns
        data_patterns = {
            "recent_data_types": {k: str(type(v).__name__) for k, v in filtered_data.items()},
            "recent_columns_used": list(filtered_data.keys()),
            "last_insertion": str(filtered_data)
        }
        
        update_ai_learning(table_name, "insertion_patterns", data_patterns)
        
        return f"✅ Inserted data into '{table_name}' (ID: {new_id})\nData: {json.dumps(filtered_data, default=str, indent=2)}"
        
    except Exception as e:
        return f"❌ Error inserting data: {str(e)}"