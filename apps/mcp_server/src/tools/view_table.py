"""View table tool - inspect table data with schema and sample rows"""

from typing import Dict, Any, List, Tuple
from ..database import db


async def handle_view_table(args: Dict[str, Any]) -> str:
    """
    View table data with schema and sample rows
    
    Shows:
    - Table schema with column descriptions
    - Total row count
    - First few rows (most recent by created_at)
    - Last few rows (oldest by created_at)
    - Clean markdown formatting
    """
    table_name = args.get("table_name")
    limit = args.get("limit", 3)  # Number of rows to show from start/end
    
    if not table_name:
        return "❌ Error: table_name is required"
    
    if not db.conn:
        return "❌ Error: Database not connected"
    
    cursor = None
    try:
        cursor = db.conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            )
        """, (table_name,))
        
        if not cursor.fetchone()[0]:
            cursor.close()
            return f"❌ Error: Table '{table_name}' does not exist"
        
        # Get table metadata
        table_info = await _get_table_info(cursor, table_name)
        
        # Get column schema
        columns = await _get_column_schema(cursor, table_name)
        
        # Get row count
        row_count = await _get_row_count(cursor, table_name)
        
        # Get sample data
        first_rows = await _get_first_rows(cursor, table_name, limit)
        last_rows = await _get_last_rows(cursor, table_name, limit)
        
        cursor.close()
        
        # Format as markdown
        markdown = _format_table_view(table_name, table_info, columns, row_count, first_rows, last_rows, limit)
        
        return markdown
        
    except Exception as e:
        if cursor:
            cursor.close()
        return f"❌ Error viewing table '{table_name}': {str(e)} (Type: {type(e).__name__})"


async def _get_table_info(cursor, table_name: str) -> Dict[str, Any]:
    """Get table metadata"""
    try:
        cursor.execute("""
            SELECT description, purpose, created_at, updated_at
            FROM _table_metadata 
            WHERE table_name = %s
        """, (table_name,))
        
        result = cursor.fetchone()
        if result:
            return {
                "description": result[0],
                "purpose": result[1], 
                "created_at": result[2],
                "updated_at": result[3]
            }
    except Exception:
        # Metadata table might not exist, return empty info
        pass
    
    return {"description": "", "purpose": "", "created_at": None, "updated_at": None}


async def _get_column_schema(cursor, table_name: str) -> List[Dict[str, Any]]:
    """Get column information with metadata"""
    # Get basic column info from information_schema
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    
    columns_basic = cursor.fetchall()
    
    # Get metadata for columns
    metadata = {}
    try:
        cursor.execute("""
            SELECT column_name, description, units
            FROM _column_metadata
            WHERE table_name = %s
        """, (table_name,))
        
        metadata = {row[0]: {"description": row[1], "units": row[2]} for row in cursor.fetchall()}
    except Exception:
        # Metadata table might not exist, continue without metadata
        pass
    
    columns = []
    for col in columns_basic:
        name, data_type, is_nullable, default = col
        meta = metadata.get(name, {})
        
        columns.append({
            "name": name,
            "type": data_type,
            "nullable": is_nullable == "YES",
            "default": default,
            "description": meta.get("description", ""),
            "units": meta.get("units", "")
        })
    
    return columns


async def _get_row_count(cursor, table_name: str) -> int:
    """Get total number of rows in table"""
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]


async def _get_first_rows(cursor, table_name: str, limit: int) -> List[Tuple]:
    """Get first few rows (most recent by created_at if available)"""
    # Check if created_at column exists
    cursor.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = %s AND column_name = 'created_at'
    """, (table_name,))
    
    has_created_at = cursor.fetchone() is not None
    
    if has_created_at:
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY created_at DESC LIMIT %s", (limit,))
    else:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT %s", (limit,))
    
    return cursor.fetchall()


async def _get_last_rows(cursor, table_name: str, limit: int) -> List[Tuple]:
    """Get last few rows (oldest by created_at if available)"""
    # Check if created_at column exists
    cursor.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = %s AND column_name = 'created_at'
    """, (table_name,))
    
    has_created_at = cursor.fetchone() is not None
    
    if has_created_at:
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY created_at ASC LIMIT %s", (limit,))
    else:
        # If no created_at, get last rows by reversing the order
        cursor.execute(f"""
            SELECT * FROM (
                SELECT * FROM {table_name} ORDER BY CTID DESC LIMIT %s
            ) sub ORDER BY CTID ASC
        """, (limit,))
    
    return cursor.fetchall()


def _format_table_view(table_name: str, table_info: Dict, columns: List[Dict], 
                      row_count: int, first_rows: List[Tuple], last_rows: List[Tuple], 
                      limit: int) -> str:
    """Format table view as markdown"""
    
    # Header
    md = f"# 📊 Table: `{table_name}`\n\n"
    
    # Table info
    if table_info.get("description"):
        md += f"**Description:** {table_info['description']}\n\n"
    if table_info.get("purpose"):
        md += f"**Purpose:** {table_info['purpose']}\n\n"
    
    md += f"**Total rows:** {row_count:,}\n\n"
    
    # Schema section
    md += "## 📋 Schema\n\n"
    md += "| Column | Type | Description | Units | Nullable | Default |\n"
    md += "|--------|------|-------------|-------|----------|----------|\n"
    
    for col in columns:
        units = f"`{col['units']}`" if col['units'] else ""
        nullable = "✅" if col['nullable'] else "❌"
        default = f"`{col['default']}`" if col['default'] else ""
        description = col['description'] or "_No description_"
        
        md += f"| `{col['name']}` | `{col['type']}` | {description} | {units} | {nullable} | {default} |\n"
    
    md += "\n"
    
    # Data sections
    if row_count > 0:
        # Get column names for headers
        col_names = [col['name'] for col in columns]
        
        # Recent data
        if first_rows:
            md += f"## 🔄 Most Recent Entries (Top {min(limit, len(first_rows))})\n\n"
            md += _format_data_table(col_names, first_rows)
            md += "\n"
        
        # Oldest data (only show if different from recent and we have enough rows)
        if last_rows and row_count > limit and last_rows != first_rows:
            md += f"## 📅 Oldest Entries (First {min(limit, len(last_rows))})\n\n"
            md += _format_data_table(col_names, last_rows)
            md += "\n"
    else:
        md += "## 📭 No Data\n\nThis table is empty.\n\n"
    
    # Footer with usage tips
    md += "---\n"
    md += f"💡 **Tips:** Use `query_data` for complex analysis or `insert_data` to add new {table_name} entries.\n"
    
    return md


def _format_data_table(col_names: List[str], rows: List[Tuple]) -> str:
    """Format rows as markdown table"""
    if not rows:
        return "_No data_\n"
    
    # Header
    md = "| " + " | ".join(col_names) + " |\n"
    md += "| " + " | ".join(["---"] * len(col_names)) + " |\n"
    
    # Data rows
    for row in rows:
        formatted_row = []
        for val in row:
            if val is None:
                formatted_row.append("_null_")
            elif isinstance(val, str) and len(val) > 50:
                formatted_row.append(f"{val[:47]}...")
            else:
                formatted_row.append(str(val))
        
        md += "| " + " | ".join(formatted_row) + " |\n"
    
    return md