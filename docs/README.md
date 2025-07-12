# Quantified Self MCP - Implementation Guide

Simple SQL-based quantified self tracking system with prompt-driven AI tools.

## Architecture Overview

**Problem**: Capture quantified self data (workouts, food, sleep) through photos/text with AI assistance.

**Solution**: 
- **MCP Tools** - AI interacts with SQL database through well-prompted tools
- **n8n Agents** - Automation pipeline processes user inputs 
- **Supabase** - PostgreSQL database for storage

## Key Components

### 1. MCP Server (AI Interface)
- `list_tables` - discover existing tables and schemas
- `create_table` - make new tables with metadata  
- `add_column` - evolve schemas naturally
- `insert_data` - store data with auto-timestamps
- `query_data` - analyze with SQL

### 2. n8n Agent Pipeline
- **Input Agent** - processes photos/text, extracts structured data
- **Extraction Agent** - uses MCP tools to store data in SQL tables
- **Analysis Agent** - generates insights with SQL queries

### 3. Database Schema
Simple SQL tables with consistent patterns:
```sql
CREATE TABLE workouts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  date TIMESTAMP NOT NULL,
  exercise TEXT NOT NULL,
  sets INTEGER,
  reps INTEGER,
  weight REAL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Implementation Steps

1. **Setup Supabase** - Create database and tables
2. **Build MCP Server** - Implement the 5 core tools
3. **Create n8n Workflow** - Set up 3-agent pipeline
4. **Test Integration** - Photo → structured data → analysis

See individual files for detailed implementation guides.