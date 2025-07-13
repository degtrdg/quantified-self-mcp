"""Quantified Self MCP Server - Dynamic table creation for quantified self tracking"""

from typing import Any, Dict, List, Optional

from agent.end_of_day_workflow import EndOfDayAnalyzer
from database import db
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tools.create_table import handle_create_table
from tools.edit_table_schema import handle_edit_table_schema
from tools.insert_data import handle_insert_data
from tools.list_tables import handle_list_tables
from tools.query_data import handle_query_data
from tools.view_table import handle_view_table

# Load environment variables
load_dotenv()

# Create FastMCP instance
mcp = FastMCP("Quantified Self MCP")


@mcp.tool()
async def list_tables(table_name: Optional[str] = None) -> str:
    """
    🔍 STEP 1: DISCOVERY - Understand existing data structure

    START HERE: Use this first to understand what's already being tracked

    WITHOUT table_name: Get overview of all tables and their purposes
    WITH table_name: Get detailed schema with column descriptions

    NEXT STEPS AFTER DISCOVERY:
    - Found relevant table? → Use `view_table` to see actual data
    - Need to modify table? → Use `edit_table_schema`
    - Need new table? → Use `create_table`
    - Ready to add data? → Use `insert_data`
    - Want to analyze? → Use `query_data`

    DECISION GUIDANCE:
    - Always start here before any operation
    - Helps decide: new table vs extend existing vs use as-is
    - Provides table names and purposes for navigation
    """
    return await handle_list_tables({"table_name": table_name})


@mcp.tool()
async def create_table(
    table_name: str,
    description: str,
    purpose: str = "",
    columns: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    🏗️ STEP 3A: CREATE - New table for entirely new data types

    USE WHEN: No existing table can accommodate the new data type

    DECISION CRITERIA:
    ✅ User wants to track something completely different (workouts vs mood vs finances)
    ✅ Data represents a distinct domain/concept
    ❌ Data could fit existing table → Use `edit_table_schema` instead
    ❌ Just adding fields to existing concept → Use `edit_table_schema` instead

    AUTO-ADDED FIELDS:
    - id: UUID primary key (automatic)
    - date: TIMESTAMP when event occurred (user provides)
    - created_at: TIMESTAMP when record created (automatic)

    COLUMN FORMAT:
    columns = [
        {"name": "exercise", "type": "TEXT", "description": "Exercise performed", "required": True},
        {"name": "weight", "type": "REAL", "description": "Weight in pounds", "units": "lbs"}
    ]

    NEXT STEPS AFTER CREATION:
    - Verify structure → Use `view_table`
    - Add data → Use `insert_data`
    - Modify later → Use `edit_table_schema`

    EXAMPLES:
    - Tracking workouts: create_table("workouts", "Exercise tracking", ...)
    - Mood tracking: create_table("mood", "Daily emotional state", ...)
    - Financial data: create_table("expenses", "Spending tracking", ...)
    """
    if columns is None:
        columns = []
    args = {
        "table_name": table_name,
        "description": description,
        "purpose": purpose,
        "columns": columns,
    }
    return await handle_create_table(args)


@mcp.tool()
async def edit_table_schema(
    table_name: str,
    operations: List[Dict[str, Any]],
) -> str:
    """
    🔧 STEP 3B: MODIFY - Comprehensive table structure editing

    USE WHEN: Existing table needs structural changes

    BEFORE USING: Run `view_table` to see current structure

    SUPPORTED OPERATIONS:
    - add_column: Add new field to existing table
    - remove_column: Remove unwanted column
    - rename_column: Improve column naming
    - change_column_type: Modify data type
    - rename_table: Rename entire table

    OPERATION FORMAT:
    operations = [
        {"action": "add_column", "name": "rpe", "type": "INTEGER", "description": "Rate of perceived exertion"},
        {"action": "rename_column", "old_name": "weight", "new_name": "weight_lbs"},
        {"action": "remove_column", "name": "deprecated_field"}
    ]

    SAFETY FEATURES:
    - Atomic execution (all succeed or all fail)
    - Transaction safety with rollback
    - Automatic metadata updates
    - Validation before execution

    NEXT STEPS AFTER EDITING:
    - Verify changes → Use `view_table`
    - Add data → Use `insert_data`
    - Query patterns → Use `query_data`

    DATA TYPES:
    - TEXT: Names, descriptions, categories
    - INTEGER: Counts, ratings, whole numbers
    - REAL: Measurements, weights, percentages
    - BOOLEAN: Yes/no, true/false values
    - TIMESTAMP: Specific times/dates
    """
    args = {
        "table_name": table_name,
        "operations": operations,
    }
    return await handle_edit_table_schema(args)


@mcp.tool()
async def insert_data(table_name: str, data: Dict[str, Any]) -> str:
    """
    💾 STEP 4: STORE - Insert quantified self data

    BEFORE INSERTING: Use `view_table` to understand expected data format

    WORKFLOW:
    1. Extract structured data from user input (photos/text/descriptions)
    2. Map data to table columns using proper field names
    3. Insert with automatic timestamps and IDs

    AUTO-HANDLED FIELDS:
    - id: UUID primary key (generated automatically)
    - created_at: Record creation timestamp (automatic)

    REQUIRED FIELD:
    - date: When the event actually occurred (user must provide)

    DATA MAPPING EXAMPLES:
    workouts: {"date": "2023-06-15 10:30", "exercise": "deadlift", "sets": 3, "reps": 5, "weight": 225}
    food: {"date": "2023-06-15 12:30", "dish_name": "chicken salad", "protein": 35, "carbs": 15}
    mood: {"date": "2023-06-15 09:00", "mood_rating": 8, "energy_level": 7, "stress_level": 3}

    IF COLUMN MISSING:
    1. Use `edit_table_schema` to add needed columns
    2. Then retry `insert_data`

    NEXT STEPS AFTER INSERTING:
    - Verify data → Use `view_table`
    - Analyze patterns → Use `query_data`
    """
    args = {"table_name": table_name, "data": data}
    return await handle_insert_data(args)


@mcp.tool()
async def view_table(table_name: str, limit: int = 3) -> str:
    """
    📊 STEP 2: INSPECT - View table structure and sample data

    USE AFTER: `list_tables` to inspect a specific table in detail

    COMPREHENSIVE VIEW:
    - Complete schema with column types and descriptions
    - Total row count and data overview
    - Recent entries (newest data)
    - Historical entries (oldest data)
    - Clean markdown formatting

    NEXT STEPS AFTER INSPECTION:
    - Schema needs changes? → Use `edit_table_schema`
    - Data looks good? → Use `insert_data` to add more
    - Want to analyze patterns? → Use `query_data`
    - Need different structure? → Use `create_table`

    PERFECT FOR:
    - Understanding data format before inserting
    - Verifying table structure after modifications
    - Quick data quality assessment
    - Seeing what data already exists

    EXAMPLES:
    - view_table("workouts") - inspect workout tracking table
    - view_table("food", 5) - see food table with more sample rows
    """
    args = {
        "table_name": table_name,
        "limit": limit,
    }
    return await handle_view_table(args)


@mcp.tool()
async def query_data(sql: str, result_format: str = "table") -> str:
    """
    📈 STEP 5: ANALYZE - Query and find patterns in your data

    USE AFTER: Data is stored and you want insights

    BEFORE QUERYING: Use `view_table` to understand available columns

    ANALYSIS PATTERNS:
    - Progress tracking: MAX, MIN, AVG over time
    - Trends: GROUP BY date, DATE_TRUNC for time windows
    - Correlations: JOIN tables on matching dates
    - Filtering: WHERE clauses for specific periods/conditions

    COMMON QUERY PATTERNS:

    Workout Progress:
    SELECT exercise, MAX(weight) as max_weight, COUNT(*) as sessions
    FROM workouts WHERE exercise = 'deadlift' GROUP BY exercise

    Cross-Domain Correlation:
    SELECT s.duration_hours, AVG(m.mood_rating) as avg_mood
    FROM sleep s JOIN mood m ON DATE(s.date) = DATE(m.date)
    GROUP BY s.duration_hours ORDER BY s.duration_hours

    Recent Trends:
    SELECT DATE(date) as day, AVG(weight) as avg_weight
    FROM workouts WHERE date >= NOW() - INTERVAL '30 days'
    GROUP BY DATE(date) ORDER BY day

    FORMAT OPTIONS:
    - "table": Markdown table (default, best for reading)
    - "json": Raw JSON (for programmatic use)
    - "summary": Key statistics with sample data

    SAFETY: Only SELECT queries allowed (read-only analysis)
    """
    args = {"sql": sql, "format": result_format}
    return await handle_query_data(args)


@mcp.tool()
async def end_of_day_analysis(focus: Optional[str] = None) -> str:
    """
    🌅 DAILY SUMMARY: Generate comprehensive end-of-day health analysis

    USE WHEN: Ready to review today's health data and get insights

    WHAT IT DOES:
    - Analyzes all quantified self data with focus on today's activities
    - Generates visualizations showing daily progress and trends
    - Uses AI to create personalized insights and recommendations
    - Sends email summary via n8n workflow

    ANALYSIS INCLUDES:
    - Today's metrics vs recent averages
    - Weekly/monthly trend analysis
    - Health score calculation across all tracked areas
    - Evidence-based recommendations using web research
    - Key achievements and areas for improvement

    EMAIL DELIVERY:
    - Sends email summary if webhook URL is configured
    - Email includes charts, insights, and actionable recommendations

    FOCUS PARAMETER (OPTIONAL):
    - Specify what to emphasize in the report analysis
    - Can be simple topics: "workout performance", "sleep quality", "nutrition goals"
    - Can be detailed observations: "I've been feeling tired after workouts and noticed my sleep has been poor. Also had headaches on days with high stress. Want to see if there are patterns between my exercise intensity, sleep quality, stress levels, and energy/mood"
    - Can include symptoms/concerns: "Experiencing digestive issues and want to correlate with food intake, meal timing, and stress levels over the past month"
    - If not provided, generates comprehensive analysis across all areas

    PERFECT FOR:
    - After the user is done inputting data for the day. You can ask them if they'd like to run an analysis.

    EXAMPLES:
    - end_of_day_analysis() - Generate comprehensive analysis
    - end_of_day_analysis("workout performance") - Focus on exercise metrics
    - end_of_day_analysis("I've been having low energy and poor sleep quality, want to see correlations with my workout timing, caffeine intake, and stress levels")
    - end_of_day_analysis("Noticed headaches on workout days - analyze exercise intensity vs recovery metrics vs hydration patterns")
    """
    import json

    import httpx

    # Analysis server URL
    server_url = "http://localhost:8000"

    try:
        # Make request to analysis server
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{server_url}/analyze", json={"focus": focus}, timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                focus_msg = f" (focus: {focus})" if focus else ""

                return f"""📊 End-of-day analysis started{focus_msg}!

🔍 Monitor progress: tail -f {result["log_file"]}

📊 Check status: curl {server_url}/status/{result["analysis_id"]}

📄 View logs: curl {server_url}/logs/{result["analysis_id"]}

📧 Check your email in 5-10 minutes for the comprehensive report.

⚠️ Note: Analysis is running on separate server. Process will continue even if this connection closes."""

            else:
                return f"❌ Failed to start analysis: HTTP {response.status_code}"

    except httpx.ConnectError:
        return f"""❌ Cannot connect to analysis server at {server_url}

🚀 Start the analysis server first:
   python analysis_server.py

📖 Then try again."""

    except Exception as e:
        return f"❌ Error starting analysis: {str(e)}"


def main():
    """Main entry point"""
    # Initialize database connection
    if not db.connect():
        print("Failed to connect to database")
        return

    print("Quantified Self MCP Server starting...")
    print("Database connected successfully")

    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()
