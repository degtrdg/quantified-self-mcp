#!/usr/bin/env python3
"""Test database connection and basic functionality."""

try:
    # Test the postgres_provider configuration
    from apps.mcp_server.src.postgres_provider import DATABASE_URL
    print("✅ Environment variables loaded successfully")
    
    # Test actual database connection
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    print("🔄 Testing database connection...")
    
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    
    # Test basic query
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ Connected to PostgreSQL: {version['version'][:50]}...")
    
    # Test if we can see tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"✅ Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table['table_name']}")
    else:
        print("ℹ️  No tables found - database is empty")
    
    # Test UUID extension
    cursor.execute("SELECT uuid_generate_v4() as test_uuid;")
    uuid_result = cursor.fetchone()
    print(f"✅ UUID extension working: {uuid_result['test_uuid']}")
    
    cursor.close()
    conn.close()
    
    print("\n🎉 Database connection test successful!")
    print("Ready to proceed with MCP server implementation.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure dependencies are installed: uv sync")
    
except EnvironmentError as e:
    print(f"❌ Environment error: {e}")
    
except psycopg2.Error as e:
    print(f"❌ Database error: {e}")
    print("Check your DATABASE_URL and network connection")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()