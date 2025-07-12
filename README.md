# Quantified Self MCP

Simple SQL-based quantified self tracking system with prompt-driven AI tools.

## What This Does

- **Captures quantified self data** (workouts, food, sleep) from photos/text
- **AI processes inputs** through MCP tools that work with SQL database
- **Evolves schema naturally** - AI adds columns as needed
- **Generates insights** through SQL analysis

## Architecture

### MCP Server (AI Interface)
5 tools that let AI work with SQL database:
- `list_tables` - discover existing data
- `create_table` - make new tables  
- `add_column` - evolve schemas
- `insert_data` - store extracted data
- `query_data` - analyze patterns

### n8n Automation (Processing Pipeline)
3 agents that handle the workflow:
- **Input Agent** - extracts data from photos/text
- **Extraction Agent** - uses MCP tools to store data
- **Analysis Agent** - generates insights with SQL

### Database (Supabase PostgreSQL)
Simple tables with consistent patterns:
```sql
CREATE TABLE workouts (
  id UUID PRIMARY KEY,
  date TIMESTAMP NOT NULL,
  exercise TEXT NOT NULL,
  sets INTEGER,
  reps INTEGER,
  weight REAL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Quick Start

1. **Setup Database**: Follow `docs/supabase-setup.md`
2. **Build MCP Server**: See `docs/mcp-server-implementation.md`  
3. **Test Integration**: Use `docs/implementation-guide.md`

## Example Workflow

**Input**: Photo of CrossFit whiteboard "21-15-9 Thrusters (95lbs), Pull-ups"

**Processing**:
1. Input Agent extracts: workout type, exercises, rep scheme, weights
2. Extraction Agent uses `list_tables()` → sees workouts table
3. Extraction Agent uses `insert_data()` → stores 6 rows (3 sets × 2 exercises)
4. Analysis Agent uses `query_data()` → finds patterns and progress

**Output**: Structured workout data + insights about progress

## Project Structure

```
spreadsheet-mcp/
├── README.md
├── docs/
│   ├── README.md                    # Architecture overview
│   ├── supabase-setup.md           # Database setup
│   ├── mcp-server-implementation.md # MCP server code
│   ├── mcp-tool-examples.md        # Tool usage patterns
│   ├── n8n-agent-prompts.md        # Agent prompt templates
│   └── implementation-guide.md     # Step-by-step guide
└── sql/
    └── sample_tables.sql           # Database schema + sample data
```

## Key Features

### Prompt-Driven AI
Each MCP tool has rich prompt context that teaches the AI:
- When to create new tables vs extend existing ones
- How to handle schema evolution gracefully  
- What constitutes good vs bad data modeling decisions

### Natural Schema Evolution
```python
# User: "I want to track RPE now"
# AI automatically:
list_tables()  # → sees workouts table
add_column("workouts", {"name": "rpe", "type": "INTEGER"})  # → adds RPE column
insert_data("workouts", {..., "rpe": 8})  # → stores workout with RPE
```

### Cross-Domain Analysis
```sql
-- Find workout performance on high-fiber days
SELECT w.exercise, w.weight, f.fiber
FROM workouts w
JOIN food f ON DATE(w.date) = DATE(f.date)  
WHERE f.fiber > 10;
```

## Ready for Hackathon

Everything your engineer needs is in the `docs/` folder:
- Complete MCP server implementation
- Supabase setup with metadata system
- n8n agent prompts for automation
- Step-by-step implementation guide

**Time Estimate**: 
- Core MCP server: 2-3 hours
- Database setup: 30 minutes  
- Basic testing: 1 hour
- n8n integration: 4-6 hours

The system is designed to be simple but powerful - normal SQL tables with AI tools that know how to use them intelligently.
