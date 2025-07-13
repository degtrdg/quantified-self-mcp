"""Test script for database helper functions"""

import sys
import os

# Add the current directory to path so we can import our modules
sys.path.append(os.path.dirname(__file__))

from database_helpers import list_tables, view_table, query_data, get_database_tools

def test_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    try:
        result = list_tables()
        if "❌" in result:
            print(f"❌ Connection failed: {result}")
            return False
        else:
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_list_tables():
    """Test list_tables function"""
    print("\n📋 Testing list_tables()...")
    try:
        result = list_tables()
        print("Result preview:", result[:200] + "..." if len(result) > 200 else result)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_query_data():
    """Test query_data function"""
    print("\n📊 Testing query_data()...")
    try:
        # Simple query to test
        result = query_data("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 3")
        print("Result preview:", result[:200] + "..." if len(result) > 200 else result)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_tool_definitions():
    """Test tool definitions"""
    print("\n🛠️ Testing tool definitions...")
    try:
        tools = get_database_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description'][:50]}...")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Database Helper Functions\n")
    
    tests = [
        ("Database Connection", test_connection),
        ("List Tables", test_list_tables), 
        ("Query Data", test_query_data),
        ("Tool Definitions", test_tool_definitions)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print(f"\n{'='*50}")
    print("📊 Test Results:")
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Helper functions are ready to use.")
    else:
        print("⚠️ Some tests failed. Check your database connection and environment setup.")

if __name__ == "__main__":
    main()