#!/usr/bin/env python3
"""Test script for database tools with mocked inputs and outputs"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

# Add the research_agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'research_agent'))

def test_explore_database():
    """Test explore_database function with mocked database"""
    print("🔍 Testing explore_database...")
    
    # Mock database responses
    mock_table_info = [
        {
            'table_name': 'workouts',
            'columns': [
                {'column_name': 'id', 'data_type': 'uuid', 'is_nullable': 'NO'},
                {'column_name': 'exercise', 'data_type': 'text', 'is_nullable': 'YES'},
                {'column_name': 'sets', 'data_type': 'integer', 'is_nullable': 'YES'},
                {'column_name': 'reps', 'data_type': 'integer', 'is_nullable': 'YES'},
                {'column_name': 'weight', 'data_type': 'numeric', 'is_nullable': 'YES'},
                {'column_name': 'created_at', 'data_type': 'timestamp', 'is_nullable': 'NO'}
            ]
        }
    ]
    
    mock_sample_data = [
        {
            'id': '123e4567-e89b-12d3-a456-426614174000',
            'exercise': 'deadlift',
            'sets': 3,
            'reps': 8,
            'weight': 225.0,
            'created_at': '2024-01-15 10:30:00'
        },
        {
            'id': '456e7890-e89b-12d3-a456-426614174001', 
            'exercise': 'bench press',
            'sets': 4,
            'reps': 6,
            'weight': 185.0,
            'created_at': '2024-01-14 11:15:00'
        }
    ]
    
    mock_count_data = [{'total_rows': 42}]
    
    with patch('research_agent.tools.database.db') as mock_db:
        # Mock the database methods
        mock_db.get_table_info.return_value = mock_table_info
        mock_db.execute_query.side_effect = [mock_sample_data, mock_count_data]
        
        from research_agent.tools.database import explore_database
        
        # Test specific table exploration
        result = explore_database('workouts')
        
        print("✅ Table exploration result:")
        print(result[:500] + "..." if len(result) > 500 else result)
        print()
        
        # Test overview of all tables
        mock_db.get_table_info.return_value = [
            {'table_name': 'workouts', 'column_count': 6},
            {'table_name': 'food', 'column_count': 8},
            {'table_name': 'sleep', 'column_count': 7}
        ]
        mock_db.execute_query.side_effect = [
            [{'total_rows': 42}],
            [{'total_rows': 156}], 
            [{'total_rows': 28}]
        ]
        
        result = explore_database()
        
        print("✅ Database overview result:")
        print(result)
        print()

def test_query_database():
    """Test query_database function with mocked SQL execution"""
    print("🔍 Testing query_database...")
    
    # Mock query results
    mock_query_results = [
        {
            'exercise': 'deadlift',
            'avg_weight': 225.5,
            'total_sessions': 12
        },
        {
            'exercise': 'bench press', 
            'avg_weight': 185.0,
            'total_sessions': 15
        },
        {
            'exercise': 'squat',
            'avg_weight': 205.0,
            'total_sessions': 10
        }
    ]
    
    with patch('research_agent.tools.database.db') as mock_db:
        mock_db.execute_query.return_value = mock_query_results
        
        from research_agent.tools.database import query_database
        
        # Test table format
        sql = "SELECT exercise, AVG(weight) as avg_weight, COUNT(*) as total_sessions FROM workouts GROUP BY exercise"
        result = query_database(sql, "table")
        
        print("✅ Query result (table format):")
        print(result)
        print()
        
        # Test JSON format
        result = query_database(sql, "json")
        
        print("✅ Query result (JSON format):")
        print(result[:300] + "..." if len(result) > 300 else result)
        print()
        
        # Test summary format
        result = query_database(sql, "summary")
        
        print("✅ Query result (summary format):")
        print(result)
        print()
        
        # Test SQL injection protection
        dangerous_sql = "DROP TABLE workouts"
        result = query_database(dangerous_sql)
        
        print("✅ SQL injection protection result:")
        print(result)
        print()

def test_database_error_handling():
    """Test error handling scenarios"""
    print("🔍 Testing database error handling...")
    
    with patch('research_agent.tools.database.db') as mock_db:
        # Mock database connection error
        mock_db.execute_query.side_effect = Exception("Connection timeout")
        
        from research_agent.tools.database import explore_database, query_database
        
        # Test explore_database error
        result = explore_database('nonexistent_table')
        print("✅ Explore database error handling:")
        print(result)
        print()
        
        # Test query_database error  
        result = query_database("SELECT * FROM workouts")
        print("✅ Query database error handling:")
        print(result)
        print()

def main():
    """Run all database tool tests"""
    print("🧪 Testing Database Tools")
    print("=" * 50)
    
    test_explore_database()
    test_query_database() 
    test_database_error_handling()
    
    print("✅ All database tool tests completed!")

if __name__ == "__main__":
    main()