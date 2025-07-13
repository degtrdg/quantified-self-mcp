from mcp import Tool
from ..database import db
from .table_metadata import get_metadata, get_all_metadata, format_ai_learnings, format_usage_patterns

LIST_TABLES_TOOL = Tool(
    name="list_tables",
    description="Shows all available tables with their purpose, schema, and recent data",
    inputSchema={
        "type": "object",
        "properties": {
            "table_name": {
                "type": "string",
                "description": "Optional: specific table name to get detailed info"
            }
        }
    }
)

async def handle_list_tables(arguments: dict) -> str:
    """
    Handle list_tables tool execution
    
    AI DECISION FRAMEWORK:
    
    ALWAYS START HERE: This is your first step for any quantified self task.
    
    WHEN YOU SEE EMPTY RESULTS:
    - No tables exist yet → User is starting fresh
    - Any new data type needs create_table 
    
    WHEN YOU SEE EXISTING TABLES:
    - Check if new data fits existing table purpose
    - Look at column descriptions to understand scope
    - Prefer extending over creating when data is related
    
    DECISION TREE:
    1. Does data fit existing table's PURPOSE? → add_column
    2. Is it completely different domain? → create_table  
    3. Unsure? → Look at detailed schema with table_name parameter
    
    EXAMPLES:
    - User mentions "workout RPE" + workouts table exists → add_column for RPE
    - User mentions "mood tracking" + no mood table → create_table for mood
    - User mentions "meditation" + no similar table → create_table for meditation
    """
    try:
        table_name = arguments.get('table_name')
        
        if table_name:
            # Get detailed info for specific table
            table_info = db.get_table_info(table_name)
            if not table_info:
                return f"Table '{table_name}' not found"
            
            info = table_info[0]
            response = f"## Table: {info['table_name']}\n"
            response += f"**Description**: {info['description']}\n"
            response += f"**Purpose**: {info['purpose']}\n\n"
            
            # Get AI metadata
            metadata = get_metadata(table_name)
            if metadata:
                if metadata['ai_learnings']:
                    response += "**🧠 AI Learnings**:\n"
                    response += format_ai_learnings(metadata['ai_learnings']) + "\n\n"
                
                if metadata['usage_patterns']:
                    response += "**📊 Usage Patterns**:\n"
                    response += format_usage_patterns(metadata['usage_patterns']) + "\n\n"
                
                if metadata['data_quality_notes']:
                    response += f"**💡 Data Quality Notes**: {metadata['data_quality_notes']}\n\n"
            
            response += "**Columns**:\n"
            for col in info['columns']:
                response += f"- `{col['column_name']}` ({col['data_type']})"
                if col['description']:
                    response += f": {col['description']}"
                if col['units']:
                    response += f" [{col['units']}]"
                response += "\n"
            
            # Get sample data
            sample_query = f"SELECT * FROM {table_name} ORDER BY created_at DESC LIMIT 3"
            sample_data = db.execute_query(sample_query)
            
            if sample_data:
                response += f"\n**Recent Data ({len(sample_data)} entries)**:\n"
                for row in sample_data:
                    response += f"- {row['date']}: {dict(row)}\n"
            
            return response
        
        else:
            # Get overview of all tables
            tables = db.get_table_info()
            all_metadata = get_all_metadata()
            
            # Create metadata lookup
            metadata_lookup = {m['table_name']: m for m in all_metadata}
            
            response = "## Available Tables\n\n"
            for table in tables:
                table_name = table['table_name']
                response += f"### {table_name}\n"
                response += f"- **Description**: {table['description']}\n"
                response += f"- **Purpose**: {table['purpose']}\n"
                response += f"- **Columns**: {table['column_count']}\n"
                
                # Add AI learnings summary if available
                if table_name in metadata_lookup:
                    metadata = metadata_lookup[table_name]
                    if metadata['ai_learnings']:
                        key_learnings = list(metadata['ai_learnings'].keys())[:3]  # Show first 3 keys
                        response += f"- **AI Insights**: {', '.join(key_learnings)}"
                        if len(metadata['ai_learnings']) > 3:
                            response += f" (+{len(metadata['ai_learnings']) - 3} more)"
                        response += "\n"
                
                response += "\n"
            
            response += "\n*Use `list_tables` with a specific table_name for detailed schema and AI learnings.*"
            
            return response
            
    except Exception as e:
        return f"Error listing tables: {str(e)}"