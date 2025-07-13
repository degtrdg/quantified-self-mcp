"""Edit table schema tool - comprehensive schema modifications"""

from typing import Dict, List, Any
from ..database import db


async def handle_edit_table_schema(args: Dict[str, Any]) -> str:
    """
    Handle comprehensive table schema editing operations
    
    Supports: add_column, remove_column, rename_column, change_column_type, rename_table
    Operations are executed atomically - all succeed or all fail
    """
    table_name = args.get("table_name")
    operations = args.get("operations", [])
    
    if not table_name:
        return "❌ Error: table_name is required"
    
    if not operations:
        return "❌ Error: operations list is required"
    
    if not db.conn:
        return "❌ Error: Database not connected"
    
    try:
        cursor = db.conn.cursor()
        
        # Start transaction for atomic operations
        cursor.execute("BEGIN;")
        
        results = []
        
        for i, operation in enumerate(operations):
            action = operation.get("action")
            
            if action == "add_column":
                result = await _add_column(cursor, table_name, operation)
                results.append(f"✅ Added column '{operation.get('name')}'")
                
            elif action == "remove_column":
                result = await _remove_column(cursor, table_name, operation)
                results.append(f"✅ Removed column '{operation.get('name')}'")
                
            elif action == "rename_column":
                result = await _rename_column(cursor, table_name, operation)
                results.append(f"✅ Renamed column '{operation.get('old_name')}' to '{operation.get('new_name')}'")
                
            elif action == "change_column_type":
                result = await _change_column_type(cursor, table_name, operation)
                results.append(f"✅ Changed column '{operation.get('name')}' type to {operation.get('new_type')}")
                
            elif action == "rename_table":
                new_name = operation.get("new_name")
                cursor.execute(f"ALTER TABLE {table_name} RENAME TO {new_name};")
                results.append(f"✅ Renamed table '{table_name}' to '{new_name}'")
                table_name = new_name  # Update for subsequent operations
                
            else:
                cursor.execute("ROLLBACK;")
                return f"❌ Error: Unknown operation '{action}' at index {i}"
        
        # Commit all operations
        cursor.execute("COMMIT;")
        
        # Update metadata for schema changes
        await _update_table_metadata(cursor, table_name)
        
        cursor.close()
        
        summary = f"✅ Successfully applied {len(operations)} schema operations to table '{table_name}':\n\n"
        summary += "\n".join(f"  {i+1}. {result}" for i, result in enumerate(results))
        
        return summary
        
    except Exception as e:
        if cursor:
            cursor.execute("ROLLBACK;")
            cursor.close()
        return f"❌ Error modifying table schema: {str(e)}"


async def _add_column(cursor, table_name: str, operation: Dict[str, Any]) -> None:
    """Add a new column to the table"""
    name = operation.get("name")
    data_type = operation.get("type", "TEXT")
    description = operation.get("description", "")
    units = operation.get("units")
    default_value = operation.get("default_value")
    required = operation.get("required", False)
    
    if not name:
        raise ValueError("Column name is required for add_column operation")
    
    # Build ALTER TABLE statement
    constraint = "NOT NULL" if required else ""
    default_clause = f"DEFAULT {default_value}" if default_value else ""
    
    alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {name} {data_type} {default_clause} {constraint};"
    cursor.execute(alter_sql)
    
    # Store column metadata
    metadata_sql = """
    INSERT INTO _column_metadata (table_name, column_name, description, units, data_type)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (table_name, column_name) DO UPDATE SET
        description = EXCLUDED.description,
        units = EXCLUDED.units,
        data_type = EXCLUDED.data_type;
    """
    cursor.execute(metadata_sql, (table_name, name, description, units, data_type))


async def _remove_column(cursor, table_name: str, operation: Dict[str, Any]) -> None:
    """Remove a column from the table"""
    name = operation.get("name")
    
    if not name:
        raise ValueError("Column name is required for remove_column operation")
    
    # Check if column exists
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = %s AND column_name = %s
    """, (table_name, name))
    
    if not cursor.fetchone():
        raise ValueError(f"Column '{name}' does not exist in table '{table_name}'")
    
    # Remove column
    cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {name};")
    
    # Remove metadata
    cursor.execute("DELETE FROM _column_metadata WHERE table_name = %s AND column_name = %s", 
                   (table_name, name))


async def _rename_column(cursor, table_name: str, operation: Dict[str, Any]) -> None:
    """Rename a column in the table"""
    old_name = operation.get("old_name")
    new_name = operation.get("new_name")
    
    if not old_name or not new_name:
        raise ValueError("Both old_name and new_name are required for rename_column operation")
    
    # Rename column
    cursor.execute(f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name};")
    
    # Update metadata
    cursor.execute("""
        UPDATE _column_metadata 
        SET column_name = %s 
        WHERE table_name = %s AND column_name = %s
    """, (new_name, table_name, old_name))


async def _change_column_type(cursor, table_name: str, operation: Dict[str, Any]) -> None:
    """Change the data type of a column"""
    name = operation.get("name")
    new_type = operation.get("new_type")
    
    if not name or not new_type:
        raise ValueError("Both name and new_type are required for change_column_type operation")
    
    # Change column type
    cursor.execute(f"ALTER TABLE {table_name} ALTER COLUMN {name} TYPE {new_type};")
    
    # Update metadata
    cursor.execute("""
        UPDATE _column_metadata 
        SET data_type = %s 
        WHERE table_name = %s AND column_name = %s
    """, (new_type, table_name, name))


async def _update_table_metadata(cursor, table_name: str) -> None:
    """Update table metadata after schema changes"""
    cursor.execute("""
        UPDATE _table_metadata 
        SET updated_at = CURRENT_TIMESTAMP 
        WHERE table_name = %s
    """, (table_name,))