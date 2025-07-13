import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
import json
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.connection_string = os.getenv('DATABASE_URL')
        if not self.connection_string:
            raise EnvironmentError(
                "DATABASE_URL environment variable is required. "
                "Please add it to your .env file. "
                "Format: postgresql://user:password@host:port/database"
            )
        self.conn = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                self.connection_string,
                cursor_factory=RealDictCursor
            )
            # Test connection
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
            print(f"✅ Database connected: {self._mask_connection_string()}")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def _mask_connection_string(self) -> str:
        """Mask sensitive parts of connection string for logging"""
        if not self.connection_string:
            return "No connection string"
        
        # Extract host for confirmation
        try:
            import re
            host_match = re.search(r'@([^:]+)', self.connection_string)
            host = host_match.group(1) if host_match else "unknown"
            return f"host={host}"
        except:
            return "connection established"
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        if not self.conn:
            if not self.connect():
                raise Exception("Failed to establish database connection")
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            print(f"❌ Query execution failed: {e}")
            self.conn.rollback()
            raise
    
    def execute_command(self, command: str, params: tuple = None) -> bool:
        """Execute an INSERT/UPDATE/DELETE command"""
        if not self.conn:
            if not self.connect():
                raise Exception("Failed to establish database connection")
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(command, params)
                self.conn.commit()
                return True
        except Exception as e:
            print(f"❌ Command execution failed: {e}")
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