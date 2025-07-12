# Quantified Self MCP - Claude Context

This is a **quantified self tracking system** that uses AI to process photos/text and store structured data in PostgreSQL through MCP tools.

## Project Overview

**Purpose**: Capture quantified self data (workouts, food, sleep, mood) from photos/text with AI assistance.

**Architecture**:
- **MCP Server** - 5 AI tools for SQL database interaction
- **n8n Agents** - 3-agent pipeline for data processing  
- **Supabase PostgreSQL** - Database with metadata system

## Core MCP Tools

The system provides 5 tools for AI interaction with the database:

1. **`list_tables`** - Discover existing tables, schemas, and recent data
2. **`create_table`** - Create new tables with metadata for new data types
3. **`add_column`** - Evolve schemas by adding columns to existing tables
4. **`insert_data`** - Store extracted data with auto-timestamps
5. **`query_data`** - Analyze patterns with SQL queries

## Database Schema Patterns

All tables follow consistent patterns:
- `id` (UUID, auto-generated)
- `date` (TIMESTAMP, when event occurred)  
- Domain-specific columns (exercise, dish_name, etc.)
- `created_at` (TIMESTAMP, when record was inserted)

### Existing Tables

- **workouts**: exercise, sets, reps, weight, duration_minutes, calories, avg_heart_rate, notes
- **food**: dish_name, protein, carbs, fats, fiber, calories, liked, meal_type
- **sleep**: bedtime, wake_time, duration_hours, quality_rating, dream_recall, notes
- **mood**: mood_rating, energy_level, stress_level, notes

## Configuration Requirements

### Environment Variables (.env)
```bash
# REQUIRED: PostgreSQL connection URL (use Supabase Transaction Pooler)
# Format for Supabase: postgresql://postgres.PROJECT_ID:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres
DATABASE_URL=postgresql://postgres.iutxhcbytqlqbmfqmbew:password@aws-0-us-east-2.pooler.supabase.com:6543/postgres

# Optional environment indicator
ENVIRONMENT=development
```

### Dependencies
- **Package Manager**: `uv` (use `uv run <script>` for all Python commands)
- `python-dotenv` - Environment variable management
- `psycopg2-binary` - PostgreSQL driver
- `mcp` - MCP server framework (when implementing server)

## Database Connection

**Supabase Setup**: Use Transaction Pooler (port 6543) for MCP servers:
- Ideal for short-lived operations and serverless functions
- IPv4 compatible for all networks
- Better connection pooling for concurrent operations

The system uses **strict error handling** with no fallbacks:
- Missing `DATABASE_URL` raises `EnvironmentError` with clear instructions
- Connection shows masked host for confirmation
- No default fallback values to prevent silent misconfigurations

**Testing**: Use `uv run tests/test_connection.py` to verify database connectivity

## Development Workflow

1. **Input Processing**: User provides photos/text of quantified self data
2. **AI Extraction**: n8n agents extract structured data using prompts
3. **Database Storage**: AI uses MCP tools to store data in appropriate tables
4. **Analysis**: AI queries data for insights and correlations

## Key Features

- **Natural Schema Evolution**: AI decides when to create new tables vs extend existing ones
- **Metadata System**: Tables and columns have descriptions to guide AI decisions
- **Cross-Domain Analysis**: SQL queries can correlate workouts, nutrition, sleep, and mood
- **Prompt-Driven**: Each tool has rich context to guide AI behavior

## Common Usage Patterns

- **New data type**: Use `create_table` with descriptive metadata
- **Extend existing**: Use `add_column` when data fits existing table
- **Store data**: Use `insert_data` after extraction
- **Find patterns**: Use `query_data` with JOINs for correlations

## Error Handling

- Database connection errors are visible and actionable
- Missing environment variables show exact setup instructions  
- SQL tool includes basic injection protection
- All tools provide detailed error messages with ❌/✅ indicators

This system is designed for hackathon-style rapid development with clean, maintainable patterns that scale.

## Claude Development Guidelines

### Command Execution
- **All Python commands**: Use `uv run <script>` pattern
- **Run from project root**: All commands should be executed from the repository root directory
- **Example**: `uv run tests/test_connection.py`

### Long-Running Tasks
- **Claude handles**: Short test scripts, database connections, file operations
- **User handles**: Long-running servers, MCP server processes, API services
- Claude should prepare/configure but not start long-running processes