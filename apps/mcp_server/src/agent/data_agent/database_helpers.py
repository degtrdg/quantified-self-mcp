"""Standalone database helper functions for data analysis agent

These functions replicate MCP tool functionality for direct database access without MCP framework.
Designed for agents that need read-only database operations and SQL querying.
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseHelper:
    """Standalone database helper for read-only operations"""
    
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self) -> bool:
        """Connect to PostgreSQL database"""
        try:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise EnvironmentError("DATABASE_URL not found in environment variables")
            
            self.connection = psycopg2.connect(
                database_url,
                cursor_factory=RealDictCursor
            )
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        if not self.connection:
            raise Exception("No database connection")
        
        try:
            with self.connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Query failed: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

# Global database helper instance - will be created on first use
db_helper = None

def get_db_helper():
    """Get database helper with connection retry"""
    global db_helper
    if db_helper is None or db_helper.connection is None or db_helper.connection.closed:
        db_helper = DatabaseHelper()
    return db_helper

def list_tables(table_name: Optional[str] = None) -> str:
    """
    🔍 DISCOVERY - Understand existing data structure
    
    WITHOUT table_name: Get overview of all tables and their purposes
    WITH table_name: Get detailed schema with column descriptions
    """
    try:
        if table_name:
            return _get_detailed_table_info(table_name)
        else:
            return _get_all_tables_overview()
    except Exception as e:
        return f"❌ Error listing tables: {str(e)}"

def _get_all_tables_overview() -> str:
    """Get overview of all tables"""
    try:
        # First get basic table info
        basic_query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND table_name NOT LIKE '%_metadata'
        ORDER BY table_name
        """
        
        basic_tables = get_db_helper().execute_query(basic_query)
        
        if not basic_tables:
            return "📊 **No tables found**\n\nUse `create_table` to start tracking quantified self data."
        
        # Get enhanced info for each table
        tables = []
        for table_row in basic_tables:
            table_name = table_row['table_name']
            
            try:
                # Get metadata if exists
                metadata_query = """
                SELECT description, purpose
                FROM table_metadata 
                WHERE table_name = %s
                """
                metadata = db_helper.execute_query(metadata_query, (table_name,))
                
                # Get column count
                column_query = """
                SELECT COUNT(*) as column_count
                FROM information_schema.columns
                WHERE table_name = %s AND table_schema = 'public'
                """
                column_info = db_helper.execute_query(column_query, (table_name,))
                
                table_info = {
                    'table_name': table_name,
                    'description': metadata[0]['description'] if metadata and len(metadata) > 0 and metadata[0]['description'] else 'No description',
                    'purpose': metadata[0]['purpose'] if metadata and len(metadata) > 0 and metadata[0]['purpose'] else 'No purpose defined',
                    'ai_learnings': '{}',  # Empty for now since ai_learnings column doesn't exist
                    'column_count': column_info[0]['column_count'] if column_info and len(column_info) > 0 else 0
                }
                tables.append(table_info)
            except Exception as e:
                print(f"Warning: Error getting info for table {table_name}: {e}")
                # Add basic info even if metadata fails
                table_info = {
                    'table_name': table_name,
                    'description': 'No description',
                    'purpose': 'No purpose defined',
                    'ai_learnings': '{}',
                    'column_count': 0
                }
                tables.append(table_info)
        
        if not tables:
            return "📊 **No tables found**\n\nUse `create_table` to start tracking quantified self data."
    
    except Exception as e:
        return f"❌ Error in _get_all_tables_overview: {str(e)}"
    
    result = ["# 📊 **Quantified Self Data Tables**\n"]
    
    for table in tables:
        ai_learnings = json.loads(table['ai_learnings']) if table['ai_learnings'] else {}
        preview = _format_ai_preview(ai_learnings)
        
        result.append(f"## 📋 **{table['table_name']}** ({table['column_count']} columns)")
        result.append(f"**Purpose**: {table['purpose']}")
        result.append(f"**Description**: {table['description']}")
        if preview:
            result.append(f"**AI Insights**: {preview}")
        result.append("")
    
    result.append("## 🎯 **Next Steps**")
    result.append("- **Inspect specific table**: Use `view_table('table_name')`")
    result.append("- **Get detailed schema**: Use `list_tables('table_name')`")
    result.append("- **Query data**: Use `query_data('SELECT ...')`")
    
    return "\n".join(result)

def _get_detailed_table_info(table_name: str) -> str:
    """Get detailed information for a specific table"""
    # Check if table exists
    table_check = db_helper.execute_query(
        "SELECT table_name FROM information_schema.tables WHERE table_name = %s AND table_schema = 'public'",
        (table_name,)
    )
    
    if not table_check:
        return f"❌ **Table '{table_name}' not found**\n\nUse `list_tables()` to see available tables."
    
    # Get table schema with metadata
    schema_query = """
    SELECT 
        c.column_name,
        c.data_type,
        c.is_nullable,
        c.column_default,
        COALESCE(cm.description, 'No description') as description,
        COALESCE(cm.units, '') as units
    FROM information_schema.columns c
    LEFT JOIN column_metadata cm ON c.table_name = cm.table_name AND c.column_name = cm.column_name
    WHERE c.table_name = %s AND c.table_schema = 'public'
    ORDER BY c.ordinal_position
    """
    
    columns = db_helper.execute_query(schema_query, (table_name,))
    
    # Get table metadata
    metadata_query = """
    SELECT description, purpose
    FROM table_metadata WHERE table_name = %s
    """
    metadata = db_helper.execute_query(metadata_query, (table_name,))
    
    result = [f"# 📋 **Table: {table_name}**\n"]
    
    # Add metadata if available
    if metadata:
        meta = metadata[0]
        result.append(f"**Purpose**: {meta['purpose'] or 'Not defined'}")
        result.append(f"**Description**: {meta['description'] or 'No description'}")
        result.append("")
    
    # Schema table
    result.append("## 📊 **Schema**")
    result.append("| Column | Type | Nullable | Default | Description | Units |")
    result.append("|--------|------|----------|---------|-------------|-------|")
    
    for col in columns:
        nullable = "Yes" if col['is_nullable'] == 'YES' else "No"
        default = col['column_default'] or ""
        units = f"({col['units']})" if col['units'] else ""
        
        result.append(f"| {col['column_name']} | {col['data_type']} | {nullable} | {default} | {col['description']} | {units} |")
    
    return "\n".join(result)

def view_table(table_name: str, limit: int = 3) -> str:
    """
    📊 INSPECT - View table structure and sample data
    
    Shows complete schema with column types, descriptions, and sample data
    """
    try:
        # Check if table exists
        table_check = db_helper.execute_query(
            "SELECT table_name FROM information_schema.tables WHERE table_name = %s AND table_schema = 'public'",
            (table_name,)
        )
        
        if not table_check:
            return f"❌ **Table '{table_name}' not found**"
        
        # Get schema
        schema_query = """
        SELECT 
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.column_default,
            COALESCE(cm.description, '') as description,
            COALESCE(cm.units, '') as units
        FROM information_schema.columns c
        LEFT JOIN column_metadata cm ON c.table_name = cm.table_name AND c.column_name = cm.column_name
        WHERE c.table_name = %s AND c.table_schema = 'public'
        ORDER BY c.ordinal_position
        """
        
        columns = db_helper.execute_query(schema_query, (table_name,))
        
        # Get row count
        count_result = db_helper.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
        total_rows = count_result[0]['count']
        
        # Get sample data (recent and oldest)
        recent_data = db_helper.execute_query(
            f"SELECT * FROM {table_name} ORDER BY created_at DESC LIMIT %s", 
            (limit,)
        )
        
        oldest_data = db_helper.execute_query(
            f"SELECT * FROM {table_name} ORDER BY created_at ASC LIMIT %s", 
            (limit,)
        )
        
        result = [f"# 📊 **Table: {table_name}** ({total_rows} rows)\n"]
        
        # Schema
        result.append("## 🏗️ **Schema**")
        result.append("| Column | Type | Nullable | Description |")
        result.append("|--------|------|----------|-------------|")
        
        for col in columns:
            nullable = "✅" if col['is_nullable'] == 'YES' else "❌"
            desc = col['description'] or "No description"
            if col['units']:
                desc += f" ({col['units']})"
            
            result.append(f"| {col['column_name']} | {col['data_type']} | {nullable} | {desc} |")
        
        # Recent data
        if recent_data:
            result.append(f"\n## 🕐 **Recent Data** (newest {len(recent_data)} entries)")
            result.append(_format_data_table(recent_data))
        
        # Oldest data  
        if oldest_data and len(oldest_data) > 0:
            result.append(f"\n## 📅 **Historical Data** (oldest {len(oldest_data)} entries)")
            result.append(_format_data_table(oldest_data))
        
        if not recent_data:
            result.append("\n📝 **No data found** - Use `insert_data` to add entries")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"❌ Error viewing table: {str(e)}"

def query_data(sql: str, result_format: str = "table") -> str:
    """
    📈 ANALYZE - Query and find patterns in your data
    
    Execute SELECT queries with multiple output formats
    """
    try:
        # Basic safety check
        sql_upper = sql.upper().strip()
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        
        if any(keyword in sql_upper for keyword in dangerous_keywords):
            return "❌ **Security Error**: Only SELECT queries are allowed for data analysis"
        
        if not sql_upper.startswith('SELECT'):
            return "❌ **Query Error**: Only SELECT queries are supported"
        
        # Execute query
        results = db_helper.execute_query(sql)
        
        if not results:
            return "📊 **Query Results**: No data found"
        
        # Format results based on requested format
        if result_format == "json":
            return _format_json_results(results)
        elif result_format == "summary":
            return _format_summary_results(results, sql)
        else:  # table format (default)
            return _format_table_results(results, sql)
            
    except Exception as e:
        return f"❌ **Query Error**: {str(e)}"

def _format_ai_preview(ai_learnings: Dict) -> str:
    """Format AI learnings preview for overview"""
    if not ai_learnings:
        return ""
    
    preview_items = []
    for key, value in list(ai_learnings.items())[:2]:  # Show first 2 items
        if isinstance(value, list):
            preview_items.append(f"{len(value)} {key}")
        elif isinstance(value, str):
            preview_items.append(f"{key}: {value[:30]}...")
    
    return ", ".join(preview_items) if preview_items else ""

def _format_ai_learnings(ai_learnings: Dict) -> str:
    """Format AI learnings for detailed display"""
    if not ai_learnings:
        return "No AI learnings yet"
    
    result = []
    for key, value in ai_learnings.items():
        if isinstance(value, list):
            result.append(f"- **{key}**: {', '.join(map(str, value))}")
        else:
            result.append(f"- **{key}**: {value}")
    
    return "\n".join(result)

def _format_data_table(data: List[Dict]) -> str:
    """Format data as markdown table"""
    if not data:
        return "No data"
    
    # Get all column names
    columns = list(data[0].keys())
    
    # Create header
    header = "| " + " | ".join(columns) + " |"
    separator = "|" + "|".join(["-" * (len(col) + 2) for col in columns]) + "|"
    
    # Create rows
    rows = []
    for row in data:
        formatted_row = []
        for col in columns:
            value = row[col]
            if value is None:
                formatted_row.append("NULL")
            else:
                # Truncate long values
                str_value = str(value)
                if len(str_value) > 47:
                    str_value = str_value[:47] + "..."
                formatted_row.append(str_value)
        
        rows.append("| " + " | ".join(formatted_row) + " |")
    
    return "\n".join([header, separator] + rows)

def _format_table_results(results: List[Dict], sql: str) -> str:
    """Format query results as table"""
    result = [f"# 📊 **Query Results** ({len(results)} rows)\n"]
    result.append(f"**Query**: `{sql}`\n")
    result.append(_format_data_table(results))
    return "\n".join(result)

def _format_json_results(results: List[Dict]) -> str:
    """Format query results as JSON"""
    # Handle datetime serialization
    import json
    from datetime import datetime, date
    
    def json_serializer(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return str(obj)
    
    return json.dumps(results, indent=2, default=json_serializer)

def _format_summary_results(results: List[Dict], sql: str) -> str:
    """Format query results as summary"""
    result = [f"# 📊 **Query Summary**\n"]
    result.append(f"**Query**: `{sql}`")
    result.append(f"**Total Rows**: {len(results)}")
    result.append(f"**Columns**: {len(results[0].keys()) if results else 0}")
    
    if results:
        result.append(f"\n## Sample Data (first 5 rows)")
        sample_data = results[:5]
        result.append(_format_data_table(sample_data))
    
    return "\n".join(result)

# Tool definitions for agent use
def get_database_tools() -> List[Dict[str, Any]]:
    """Get tool definitions for agent use"""
    return [
        {
            "name": "list_tables",
            "description": "🔍 DISCOVERY - Understand existing data structure. Use without table_name for overview, with table_name for detailed schema.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string", 
                        "description": "Optional: specific table name for detailed view"
                    }
                }
            }
        },
        {
            "name": "view_table", 
            "description": "📊 INSPECT - View table structure and sample data with schema details and recent/historical entries.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of table to inspect"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of sample rows to show (default: 3)",
                        "default": 3
                    }
                },
                "required": ["table_name"]
            }
        },
        {
            "name": "query_data",
            "description": "📈 ANALYZE - Execute SELECT queries to find patterns and analyze data. Supports table, json, and summary output formats.",
            "input_schema": {
                "type": "object", 
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SELECT SQL query to execute"
                    },
                    "result_format": {
                        "type": "string",
                        "description": "Output format: 'table' (default), 'json', or 'summary'",
                        "enum": ["table", "json", "summary"],
                        "default": "table"
                    }
                },
                "required": ["sql"]
            }
        },
        {
            "name": "final_query",
            "description": "Use this tool to come up with a final query to run on the database. This will end your session and create a csv file with the results to go to a report agent who will run analyses on the data with matplotlib.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string", 
                        "description": "The SQL query to run on the database"
                    }
                },
                "required": ["query"]
            }
        }
    ]

# Function mapping for tool execution
TOOL_FUNCTIONS = {
    "list_tables": list_tables,
    "view_table": view_table, 
    "query_data": query_data
}

def execute_tool(tool_name: str, **kwargs) -> str:
    """Execute a tool function by name"""
    if tool_name not in TOOL_FUNCTIONS:
        return f"❌ Unknown tool: {tool_name}"
    
    try:
        return TOOL_FUNCTIONS[tool_name](**kwargs)
    except Exception as e:
        return f"❌ Tool execution error: {str(e)}"