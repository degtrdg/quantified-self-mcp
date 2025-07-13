from mcp import Tool
from ..database import db

CREATE_TABLE_TOOL = Tool(
    name="create_table",
    description="Creates a new table with columns and metadata",
    inputSchema={
        "type": "object",
        "properties": {
            "table_name": {
                "type": "string",
                "description": "Name of the table to create"
            },
            "description": {
                "type": "string", 
                "description": "Description of what this table tracks"
            },
            "purpose": {
                "type": "string",
                "description": "The purpose/goal of tracking this data"
            },
            "columns": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "description": {"type": "string"},
                        "units": {"type": "string"},
                        "required": {"type": "boolean"}
                    },
                    "required": ["name", "type", "description"]
                }
            }
        },
        "required": ["table_name", "description", "columns"]
    }
)

async def handle_create_table(arguments: dict) -> str:
    """
    Handle create_table tool execution
    
    AI SCHEMA DESIGN GUIDANCE:
    
    BEFORE CREATING - ASK YOURSELF:
    1. Is this a fundamentally different DATA DOMAIN?
       ✓ Workouts vs Sleep vs Mood vs Finances (different domains)
       ✗ Adding RPE to workouts (same domain, different metric)
    
    2. Does it have its OWN TEMPORAL PATTERN?
       ✓ Daily mood entries vs individual workout sessions
       ✗ Workout intensity (happens during workouts)
    
    3. Would it STANDALONE for analysis?
       ✓ "Show me my sleep patterns" (sleep table)
       ✗ "Show me workout intensity" (column in workouts)
    
    COLUMN DESIGN PRINCIPLES:
    - Use clear, unambiguous names (exercise not type)
    - Include units in description, not column name
    - Mark required fields with "required": True
    - Add units for measurements ("lbs", "minutes", "scale_1_10")
    
    SEMANTIC NAMING:
    - Events: workouts, meals, sleep_sessions
    - States: mood, energy, symptoms  
    - Measurements: weight, blood_pressure, steps
    - Activities: meditation, reading, social_interactions
    """
    try:
        table_name = arguments['table_name']
        description = arguments['description']
        purpose = arguments.get('purpose', '')
        columns = arguments['columns']
        
        # Build CREATE TABLE statement
        sql_columns = [
            "id UUID PRIMARY KEY DEFAULT uuid_generate_v4()",
            "date TIMESTAMP NOT NULL",
        ]
        
        # Add custom columns
        for col in columns:
            col_def = f"{col['name']} {col['type']}"
            if col.get('required', False):
                col_def += " NOT NULL"
            sql_columns.append(col_def)
        
        # Always add created_at
        sql_columns.append("created_at TIMESTAMP DEFAULT NOW()")
        
        create_sql = f"""
        CREATE TABLE {table_name} (
            {', '.join(sql_columns)}
        )
        """
        
        # Execute table creation
        db.execute_command(create_sql)
        
        # Add table metadata
        metadata_sql = """
        INSERT INTO table_metadata (table_name, description, purpose) 
        VALUES (%s, %s, %s)
        """
        db.execute_command(metadata_sql, (table_name, description, purpose))
        
        # Add column metadata
        for col in columns:
            col_metadata_sql = """
            INSERT INTO column_metadata (table_name, column_name, description, data_type, units) 
            VALUES (%s, %s, %s, %s, %s)
            """
            db.execute_command(col_metadata_sql, (
                table_name, 
                col['name'], 
                col['description'], 
                col['type'],
                col.get('units')
            ))
        
        return f"✅ Created table '{table_name}' with {len(columns)} custom columns plus standard fields (id, date, created_at)"
        
    except Exception as e:
        return f"❌ Error creating table: {str(e)}"