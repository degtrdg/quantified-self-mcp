# MCP Server Implementation Guide

Complete guide for building the MCP server with prompt-driven SQL tools.

## Project Structure

```
mcp-server/
├── src/
│   ├── __init__.py
│   ├── server.py          # Main MCP server
│   ├── database.py        # Database connection and utilities
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── list_tables.py
│   │   ├── create_table.py
│   │   ├── add_column.py
│   │   ├── insert_data.py
│   │   └── query_data.py
│   └── prompts/
│       ├── __init__.py
│       └── tool_prompts.py
├── requirements.txt
├── pyproject.toml
└── .env
```

## 1. Dependencies

### requirements.txt
```txt
mcp>=1.0.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
asyncio>=3.4.3
```

### pyproject.toml
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "quantified-self-mcp"
version = "0.1.0"
description = "MCP server for quantified self SQL database"
dependencies = [
    "mcp>=1.0.0",
    "psycopg2-binary>=2.9.0", 
    "python-dotenv>=1.0.0"
]

[project.scripts]
quantified-self-mcp = "src.server:main"
```

## 2. Database Connection

### src/database.py
```python
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
import json

class DatabaseConnection:
    def __init__(self):
        self.connection_string = os.getenv('DATABASE_URL')
        self.conn = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                self.connection_string,
                cursor_factory=RealDictCursor
            )
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        if not self.conn:
            self.connect()
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            print(f"Query execution failed: {e}")
            self.conn.rollback()
            raise
    
    def execute_command(self, command: str, params: tuple = None) -> bool:
        """Execute an INSERT/UPDATE/DELETE command"""
        if not self.conn:
            self.connect()
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(command, params)
                self.conn.commit()
                return True
        except Exception as e:
            print(f"Command execution failed: {e}")
            self.conn.rollback()
            raise
    
    def get_table_info(self, table_name: str = None) -> List[Dict[str, Any]]:
        """Get table information with metadata"""
        if table_name:
            query = """
            SELECT 
                t.table_name,
                t.description,
                t.purpose,
                json_agg(
                    json_build_object(
                        'column_name', c.column_name,
                        'data_type', c.data_type,
                        'description', cm.description,
                        'units', cm.units
                    ) ORDER BY c.ordinal_position
                ) as columns
            FROM table_metadata t
            LEFT JOIN information_schema.columns c ON t.table_name = c.table_name
            LEFT JOIN column_metadata cm ON (c.table_name = cm.table_name AND c.column_name = cm.column_name)
            WHERE t.table_name = %s AND c.table_schema = 'public'
            GROUP BY t.table_name, t.description, t.purpose
            """
            return self.execute_query(query, (table_name,))
        else:
            query = """
            SELECT 
                t.table_name,
                t.description,
                t.purpose,
                COUNT(c.column_name) as column_count
            FROM table_metadata t
            LEFT JOIN information_schema.columns c ON t.table_name = c.table_name
            WHERE c.table_schema = 'public'
            GROUP BY t.table_name, t.description, t.purpose
            ORDER BY t.table_name
            """
            return self.execute_query(query)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Global database instance
db = DatabaseConnection()
```

## 3. Tool Implementations

### src/tools/list_tables.py
```python
from mcp.server.models import Tool
from mcp.server import NotificationOptions
from mcp.types import *
from ..database import db

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
    
    Prompt Context: Use this to understand what data is already being tracked. 
    Each table represents a different type of quantified self data (workouts, 
    food, sleep, etc.). Look at the table metadata to understand the purpose 
    and existing columns before deciding whether to create a new table or add 
    to an existing one.
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
            
            response = "## Available Tables\n\n"
            for table in tables:
                response += f"### {table['table_name']}\n"
                response += f"- **Description**: {table['description']}\n"
                response += f"- **Purpose**: {table['purpose']}\n"
                response += f"- **Columns**: {table['column_count']}\n\n"
            
            response += "\n*Use `list_tables` with a specific table_name for detailed schema information.*"
            
            return response
            
    except Exception as e:
        return f"Error listing tables: {str(e)}"
```

### src/tools/create_table.py
```python
from mcp.server.models import Tool
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
    
    Prompt Context: When users want to track something new that doesn't fit 
    existing tables, create a new table. Always include: id (UUID), date 
    (TIMESTAMP), created_at (TIMESTAMP). Use descriptive column names and add 
    metadata explaining the table's purpose. Ask yourself: is this really new 
    data or could it be added to an existing table?
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
```

### src/tools/add_column.py
```python
from mcp.server.models import Tool
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
    
    Prompt Context: When users mention tracking something new that fits an 
    existing table, add a column rather than creating a new table. Always add 
    a description of what the column represents. Consider data types carefully 
    (TEXT, INTEGER, REAL, BOOLEAN, TIMESTAMP).
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
```

### src/tools/insert_data.py
```python
from mcp.server.models import Tool
from ..database import db
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
    
    Prompt Context: Insert extracted data into the appropriate table. The id 
    and created_at fields are automatically handled. Focus on mapping the 
    user's input to the correct columns. If a column doesn't exist that you 
    need, use add_column first.
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
        result = db.execute_query(insert_sql, tuple(values))
        new_id = result[0]['id'] if result else None
        
        return f"✅ Inserted data into '{table_name}' (ID: {new_id})\nData: {json.dumps(filtered_data, default=str, indent=2)}"
        
    except Exception as e:
        return f"❌ Error inserting data: {str(e)}"
```

### src/tools/query_data.py
```python
from mcp.server.models import Tool
from ..database import db
import json

QUERY_DATA_TOOL = Tool(
    name="query_data",
    description="Execute SQL queries and format results",
    inputSchema={
        "type": "object",
        "properties": {
            "sql": {
                "type": "string",
                "description": "SQL query to execute"
            },
            "format": {
                "type": "string",
                "enum": ["table", "json", "summary"],
                "description": "How to format the results",
                "default": "table"
            }
        },
        "required": ["sql"]
    }
)

async def handle_query_data(arguments: dict) -> str:
    """
    Handle query_data tool execution
    
    Prompt Context: Use standard SQL to query across tables. You can JOIN 
    tables to find correlations (e.g., workout performance vs nutrition). 
    Format results in a human-readable way. Common patterns: aggregations by 
    date, filtering by date ranges, finding correlations.
    """
    try:
        sql = arguments['sql']
        format_type = arguments.get('format', 'table')
        
        # Basic SQL injection protection (enhance for production)
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE']
        sql_upper = sql.upper()
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return f"❌ {keyword} operations are not allowed"
        
        # Execute query
        results = db.execute_query(sql)
        
        if not results:
            return "No results found."
        
        if format_type == "json":
            return json.dumps(results, default=str, indent=2)
        
        elif format_type == "summary":
            response = f"## Query Results\n\n"
            response += f"**Rows returned**: {len(results)}\n"
            response += f"**Columns**: {', '.join(results[0].keys())}\n\n"
            
            # Show first few rows
            for i, row in enumerate(results[:5]):
                response += f"**Row {i+1}**: {dict(row)}\n"
            
            if len(results) > 5:
                response += f"\n... and {len(results) - 5} more rows"
            
            return response
        
        else:  # table format
            if not results:
                return "No data found."
            
            # Create markdown table
            headers = list(results[0].keys())
            response = "| " + " | ".join(headers) + " |\n"
            response += "|" + "|".join([" --- "] * len(headers)) + "|\n"
            
            for row in results:
                values = [str(row[header]) if row[header] is not None else "" for header in headers]
                response += "| " + " | ".join(values) + " |\n"
            
            response += f"\n*{len(results)} rows returned*"
            
            return response
        
    except Exception as e:
        return f"❌ Error executing query: {str(e)}"
```

## 4. Main Server

### src/server.py
```python
import asyncio
import os
from dotenv import load_dotenv
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import *

from .database import db
from .tools.list_tables import LIST_TABLES_TOOL, handle_list_tables
from .tools.create_table import CREATE_TABLE_TOOL, handle_create_table
from .tools.add_column import ADD_COLUMN_TOOL, handle_add_column
from .tools.insert_data import INSERT_DATA_TOOL, handle_insert_data
from .tools.query_data import QUERY_DATA_TOOL, handle_query_data

# Load environment variables
load_dotenv()

# Create server instance
server = Server("quantified-self-mcp")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        LIST_TABLES_TOOL,
        CREATE_TABLE_TOOL, 
        ADD_COLUMN_TOOL,
        INSERT_DATA_TOOL,
        QUERY_DATA_TOOL
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool execution"""
    try:
        if name == "list_tables":
            result = await handle_list_tables(arguments)
        elif name == "create_table":
            result = await handle_create_table(arguments)
        elif name == "add_column":
            result = await handle_add_column(arguments)
        elif name == "insert_data":
            result = await handle_insert_data(arguments)
        elif name == "query_data":
            result = await handle_query_data(arguments)
        else:
            result = f"❌ Unknown tool: {name}"
        
        return [TextContent(type="text", text=result)]
    
    except Exception as e:
        error_msg = f"❌ Error executing {name}: {str(e)}"
        return [TextContent(type="text", text=error_msg)]

async def main():
    """Main entry point"""
    # Initialize database connection
    if not db.connect():
        print("Failed to connect to database")
        return
    
    print("Quantified Self MCP Server starting...")
    print("Database connected successfully")
    
    # Run the server
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="quantified-self-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## 5. Running the Server

### Start the server:
```bash
cd mcp-server
python -m src.server
```

### Test with Claude Desktop:
Add to Claude Desktop config:
```json
{
  "mcpServers": {
    "quantified-self": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/mcp-server"
    }
  }
}
```

The MCP server is now ready to handle quantified self data with prompt-driven AI interactions!