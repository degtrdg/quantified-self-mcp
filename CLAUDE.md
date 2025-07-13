# Quantified Self MCP - Claude Context

This is a **quantified self tracking system** that uses AI to process photos/text and store structured data in PostgreSQL through MCP tools.

## Project Overview

**Purpose**: Capture quantified self data (workouts, food, sleep, mood) from photos/text with AI assistance.

**Architecture**:
- **MCP Server** - 6 AI tools for SQL database interaction with metadata learning system
- **n8n Agents** - 3-agent pipeline for data processing  
- **Supabase PostgreSQL** - Database with AI learning and metadata system

## Core MCP Tools

The system provides 6 tools for AI interaction with the database:

1. **`list_tables`** - Discover existing tables, schemas, AI learnings, and recent data
2. **`create_table`** - Create new tables with metadata for new data types
3. **`edit_table_schema`** - Evolve schemas by adding/removing/modifying columns
4. **`view_table`** - Inspect table structure and sample data in detail
5. **`insert_data`** - Store extracted data with auto-timestamps and AI learning updates
6. **`query_data`** - Analyze patterns with SQL queries

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
- **AI Learning & Memory System**: Tables store metadata and AI learnings for improved decision-making
- **Cross-Domain Analysis**: SQL queries can correlate workouts, nutrition, sleep, and mood
- **Metadata-Driven Intelligence**: Each table accumulates knowledge about data patterns, usage, and context
- **Prompt-Driven**: Each tool has rich context to guide AI behavior

## AI Learning & Memory System

The system includes a **table_metadata** table that stores AI learnings and usage patterns:

**Metadata Structure**:
- `table_name` - Links to actual data table
- `description` & `purpose` - Human-readable context
- `ai_learnings` - JSON of accumulated AI insights about the table
- `usage_patterns` - JSON of observed data patterns and user behaviors
- `data_quality_notes` - Notes about data quality and common issues

**AI Learning Examples**:
```json
{
  "common_exercises": ["deadlift", "bench_press", "squat"],
  "weight_units": "lbs", 
  "typical_rep_ranges": "3-10 reps per set",
  "data_patterns": "Users track compound movements most consistently"
}
```

**How AI Learning Works**:
1. **Table Creation**: Initial context stored when creating tables
2. **Data Insertion**: Patterns learned from each data insertion
3. **Schema Changes**: Reasons for modifications tracked
4. **Query Analysis**: Frequently accessed data patterns noted
5. **User Feedback**: Quality issues and preferences recorded

**Memory Benefits**:
- **Better Decisions**: AI knows which tables to use vs create new ones
- **Context Awareness**: Understanding of data types, units, and patterns
- **Quality Improvement**: Learning from past insertion successes/failures
- **Usage Optimization**: Adapting to user's specific tracking preferences

## Common Usage Patterns

- **New data type**: Use `create_table` with descriptive metadata and initial AI context
- **Extend existing**: Use `edit_table_schema` when data fits existing table purpose  
- **Store data**: Use `insert_data` after extraction (automatically updates AI learnings)
- **Find patterns**: Use `query_data` with JOINs for correlations
- **Review context**: Use `list_tables` with table name to see all AI learnings

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