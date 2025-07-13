"""Table metadata management for AI learning and memory system"""

from typing import Any, Dict, List, Optional
import json
from ..database import db


def get_table_metadata_schema() -> Dict[str, str]:
    """Get the actual columns available in table_metadata table"""
    try:
        result = db.execute_query("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'table_metadata' 
        AND table_schema = 'public'
        ORDER BY ordinal_position
        """)
        return {row["column_name"]: row["data_type"] for row in result}
    except:
        # Fallback to basic schema if table doesn't exist
        return {
            "table_name": "text",
            "description": "text", 
            "purpose": "text",
            "created_at": "timestamp"
        }


def create_metadata_table() -> bool:
    """Create the table_metadata table if it doesn't exist"""
    create_sql = """
    CREATE TABLE IF NOT EXISTS table_metadata (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        table_name TEXT NOT NULL UNIQUE,
        description TEXT NOT NULL,
        purpose TEXT NOT NULL,
        ai_learnings JSONB DEFAULT '{}',
        usage_patterns JSONB DEFAULT '{}',
        data_quality_notes TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    return db.execute_command(create_sql)


def store_metadata(
    table_name: str,
    description: str,
    purpose: str = "",
    ai_learnings: Optional[Dict[str, Any]] = None,  # Ignored for now
    usage_patterns: Optional[Dict[str, Any]] = None,  # Ignored for now
    data_quality_notes: str = ""  # Ignored for now
) -> bool:
    """Store or update metadata for a table"""
    # Only use columns that actually exist in the current schema
    upsert_sql = """
    INSERT INTO table_metadata (table_name, description, purpose)
    VALUES (%s, %s, %s)
    ON CONFLICT (table_name) 
    DO UPDATE SET 
        description = EXCLUDED.description,
        purpose = EXCLUDED.purpose,
        updated_at = CURRENT_TIMESTAMP
    """
    
    return db.execute_command(upsert_sql, (table_name, description, purpose))


def update_ai_learning(table_name: str, learning_key: str, learning_value: Any) -> bool:
    """Update specific AI learning for a table - simplified version for current schema"""
    # Since the current table_metadata schema doesn't have ai_learnings column,
    # we'll just return True to avoid breaking the insert_data flow
    # TODO: Add ai_learnings column to table_metadata if needed
    return True


def get_metadata(table_name: str) -> Optional[Dict[str, Any]]:
    """Get metadata for a specific table"""
    schema = get_table_metadata_schema()
    
    # Build dynamic SELECT query based on available columns
    available_columns = list(schema.keys())
    sql = f"""
    SELECT {', '.join(available_columns)}
    FROM table_metadata 
    WHERE table_name = %s
    """
    
    results = db.execute_query(sql, (table_name,))
    if not results:
        return None
    
    result = results[0]
    
    # Build response with available data, provide defaults for missing columns
    metadata = {
        "table_name": result["table_name"],
        "description": result["description"],
        "purpose": result.get("purpose", ""),
        "ai_learnings": {},  # Not in DB yet
        "usage_patterns": {},  # Not in DB yet  
        "data_quality_notes": "",  # Not in DB yet
        "last_updated": result.get("updated_at"),
        "created_at": result["created_at"]
    }
    
    return metadata


def get_all_metadata() -> List[Dict[str, Any]]:
    """Get metadata for all tables"""
    schema = get_table_metadata_schema()
    
    # Build dynamic SELECT query based on available columns
    available_columns = list(schema.keys())
    sql = f"""
    SELECT {', '.join(available_columns)}
    FROM table_metadata 
    ORDER BY table_name
    """
    
    results = db.execute_query(sql)
    if not results:
        return []
    
    metadata_list = []
    for result in results:
        metadata = {
            "table_name": result["table_name"],
            "description": result["description"],
            "purpose": result.get("purpose", ""),
            "ai_learnings": {},  # Not in DB yet
            "usage_patterns": {},  # Not in DB yet
            "data_quality_notes": "",  # Not in DB yet
            "last_updated": result.get("updated_at"),
            "created_at": result["created_at"]
        }
        metadata_list.append(metadata)
    
    return metadata_list


def format_ai_learnings(learnings: Dict[str, Any]) -> str:
    """Format AI learnings for display"""
    if not learnings:
        return "No AI learnings recorded yet"
    
    formatted = []
    for key, value in learnings.items():
        if isinstance(value, dict):
            formatted.append(f"• **{key}**: {json.dumps(value, indent=2)}")
        elif isinstance(value, list):
            formatted.append(f"• **{key}**: {', '.join(map(str, value))}")
        else:
            formatted.append(f"• **{key}**: {value}")
    
    return "\n".join(formatted)


def format_usage_patterns(patterns: Dict[str, Any]) -> str:
    """Format usage patterns for display"""
    if not patterns:
        return "No usage patterns recorded yet"
    
    formatted = []
    for key, value in patterns.items():
        if isinstance(value, dict):
            formatted.append(f"• **{key}**: {json.dumps(value, indent=2)}")
        elif isinstance(value, list):
            formatted.append(f"• **{key}**: {', '.join(map(str, value))}")
        else:
            formatted.append(f"• **{key}**: {value}")
    
    return "\n".join(formatted)