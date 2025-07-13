from mcp import Tool
from ..database import db

ADD_COLUMN_TOOL = Tool(
    name="add_column",
    description="Adds new column to existing table with description",
    inputSchema={
        "type": "object",
        "properties": {
            "table_name": {
                "type": "string",
                "description": "Name of the table to modify"
            },
            "column_name": {
                "type": "string",
                "description": "Name of the new column"
            },
            "data_type": {
                "type": "string",
                "description": "PostgreSQL data type (TEXT, INTEGER, REAL, BOOLEAN, TIMESTAMP)"
            },
            "description": {
                "type": "string",
                "description": "Description of what this column represents"
            },
            "units": {
                "type": "string",
                "description": "Units of measurement (optional)"
            },
            "default_value": {
                "type": "string",
                "description": "Default value (optional)"
            }
        },
        "required": ["table_name", "column_name", "data_type", "description"]
    }
)

async def handle_add_column(arguments: dict) -> str:
    """
    Handle add_column tool execution
    
    AI SCHEMA EVOLUTION GUIDANCE:
    
    WHEN TO CHOOSE add_column OVER create_table:
    - User says "I also want to track [X] for my workouts"
    - New metric belongs to existing activity/concept
    - Data would be analyzed together with existing columns
    - It's an ATTRIBUTE of something already tracked
    
    DATA TYPE DECISION TREE:
    
    TEXT: 
    - Categories (beginner/intermediate/advanced)
    - Names (gym_name, trainer_name)
    - Notes/descriptions (workout_notes)
    
    INTEGER:
    - Counts (sets, reps, days)  
    - Ratings/scales (rpe_1_10, mood_1_10)
    - Whole number measurements (heart_rate_bpm)
    
    REAL (decimal numbers):
    - Weights (225.5)
    - Percentages (body_fat_percent) 
    - Precise measurements (duration_hours: 7.5)
    
    BOOLEAN:
    - Yes/no questions (felt_good, used_supplements)
    - Binary states (fasted, outdoors)
    
    TIMESTAMP:
    - Specific times (start_time, end_time)
    - Only when different from main 'date' field
    
    NAMING CONVENTIONS:
    - Use underscores: heart_rate not heartRate
    - Be specific: weight_lbs not weight
    - Include scale: rpe_1_10, mood_1_10
    """
    try:
        table_name = arguments['table_name']
        column_name = arguments['column_name']
        data_type = arguments['data_type']
        description = arguments['description']
        units = arguments.get('units')
        default_value = arguments.get('default_value')
        
        # Check if table exists
        table_check = db.execute_query(
            "SELECT table_name FROM information_schema.tables WHERE table_name = %s",
            (table_name,)
        )
        if not table_check:
            return f"❌ Table '{table_name}' does not exist"
        
        # Check if column already exists
        col_check = db.execute_query(
            "SELECT column_name FROM information_schema.columns WHERE table_name = %s AND column_name = %s",
            (table_name, column_name)
        )
        if col_check:
            return f"❌ Column '{column_name}' already exists in table '{table_name}'"
        
        # Build ALTER TABLE statement
        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {data_type}"
        if default_value:
            alter_sql += f" DEFAULT {default_value}"
        
        # Execute column addition
        db.execute_command(alter_sql)
        
        # Add column metadata
        metadata_sql = """
        INSERT INTO column_metadata (table_name, column_name, description, data_type, units) 
        VALUES (%s, %s, %s, %s, %s)
        """
        db.execute_command(metadata_sql, (table_name, column_name, description, data_type, units))
        
        return f"✅ Added column '{column_name}' ({data_type}) to table '{table_name}'"
        
    except Exception as e:
        return f"❌ Error adding column: {str(e)}"