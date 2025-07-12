# Implementation Guide - Getting Started

Step-by-step guide to get your quantified self MCP system running.

## Quick Start (for Hackathon)

### 1. Setup Supabase Database (15 minutes)
```bash
# 1. Create Supabase account and project
# 2. Run setup SQL from docs/supabase-setup.md
# 3. Get your connection credentials
```

### 2. Build MCP Server (30 minutes)
```bash
# Clone/create project structure
mkdir quantified-self-mcp
cd quantified-self-mcp

# Set up Python environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install mcp psycopg2-binary python-dotenv

# Create .env file with your Supabase credentials
echo "DATABASE_URL=postgresql://postgres:password@db.project.supabase.co:5432/postgres" > .env

# Copy MCP server code from docs/mcp-server-implementation.md
# Test connection
python src/server.py
```

### 3. Test Basic Functionality (15 minutes)
```bash
# Test with Claude Desktop (add to config):
{
  "mcpServers": {
    "quantified-self": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/quantified-self-mcp"
    }
  }
}

# Test tools:
# 1. list_tables() - should show workouts, food, sleep, mood
# 2. insert_data() - add a sample workout
# 3. query_data() - query the data back
```

## Full Implementation Steps

### Phase 1: Core MCP Server (Day 1)
- [x] Supabase setup with metadata tables
- [x] MCP server with 5 core tools
- [x] Database connection and error handling
- [x] Basic testing with Claude Desktop

**Files to implement:**
- `src/server.py` - main MCP server
- `src/database.py` - database utilities
- `src/tools/` - all 5 tool implementations

### Phase 2: n8n Automation (Day 2) 
- [ ] n8n workspace setup
- [ ] Input Agent (photo/text processing)
- [ ] Extraction Agent (MCP tool integration)
- [ ] Analysis Agent (insights generation)

**n8n Workflow:**
1. Webhook receives user input
2. Input Agent processes and extracts data
3. Extraction Agent stores in database
4. Analysis Agent generates insights
5. Return formatted response

### Phase 3: Testing & Polish (Day 3)
- [ ] End-to-end testing (photo → analysis)
- [ ] Error handling and edge cases
- [ ] Performance optimization
- [ ] Documentation and demo prep

## Key Implementation Notes

### Database Schema Rules
Every table must have:
```sql
id UUID PRIMARY KEY DEFAULT uuid_generate_v4()
date TIMESTAMP NOT NULL  -- when the event occurred
created_at TIMESTAMP DEFAULT NOW()  -- when recorded
```

### MCP Tool Patterns
1. **Always check existing tables first** with `list_tables()`
2. **Prefer extending over creating** - add columns vs new tables
3. **Rich prompt context** guides AI behavior
4. **Consistent error handling** with clear messages

### n8n Agent Design
- **Input Agent**: Extract structured data from photos/text
- **Extraction Agent**: Use MCP tools to store data
- **Analysis Agent**: Generate insights with SQL queries

### Claude Integration
The prompts are designed to work with Claude's reasoning patterns:
- Clear context about when to use each tool
- Specific examples of good vs bad decisions
- Error handling guidance
- Consistent output formatting

## Testing Strategy

### Unit Tests
```python
# Test database connection
def test_db_connection():
    assert db.connect() == True

# Test MCP tools
def test_list_tables():
    result = await handle_list_tables({})
    assert "workouts" in result

# Test data insertion
def test_insert_workout():
    data = {"date": "2023-06-08", "exercise": "deadlift", "weight": 185}
    result = await handle_insert_data({"table_name": "workouts", "data": data})
    assert "✅" in result
```

### Integration Tests
```python
# Test full workflow
def test_photo_to_database():
    # 1. Mock photo input
    # 2. Process with Input Agent
    # 3. Store with Extraction Agent
    # 4. Query back with Analysis Agent
    # 5. Verify data consistency
```

### Demo Scenarios
1. **CrossFit Workout**: Photo of whiteboard → structured workout data
2. **Food Logging**: Text description → nutrition tracking
3. **Schema Evolution**: New metric → automatic column addition
4. **Analysis**: Query patterns and generate insights

## Production Considerations

### Security
- Row Level Security (RLS) for multi-user support
- Input validation and SQL injection prevention
- API rate limiting and authentication

### Performance
- Database indexing for common queries
- Connection pooling for MCP server
- Caching for frequently accessed data

### Monitoring
- Error logging and alerting
- Usage analytics and performance metrics
- Database health monitoring

Your engineer now has everything needed to implement the system!