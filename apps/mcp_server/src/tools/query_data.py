from mcp import Tool
from ..database import db
import json

QUERY_DATA_TOOL = Tool(
    name="query_data",
    description="Execute SQL queries and format results",
    inputSchema={
        "type": "object",
        "properties": {
            "sql": {
                "type": "string",
                "description": "SQL query to execute"
            },
            "format": {
                "type": "string",
                "enum": ["table", "json", "summary"],
                "description": "How to format the results",
                "default": "table"
            }
        },
        "required": ["sql"]
    }
)

async def handle_query_data(arguments: dict) -> str:
    """
    Handle query_data tool execution
    
    AI ANALYTICS & INSIGHT GUIDANCE:
    
    ANALYSIS PATTERNS FOR QUANTIFIED SELF:
    
    PROGRESS TRACKING:
    - Time series: GROUP BY DATE(date) ORDER BY date
    - Maximums: MAX(weight), MAX(duration), etc.
    - Moving averages: Use window functions
    
    CORRELATION ANALYSIS:
    - Cross-domain: JOIN sleep s ON DATE(s.date) = DATE(w.date)
    - Same-day events: Match on DATE(date)
    - Weekly patterns: DATE_PART('dow', date) for day of week
    
    COMPARATIVE ANALYSIS:
    - Percentiles: PERCENTILE_CONT(0.5) for medians
    - Rankings: RANK() OVER (ORDER BY metric DESC)
    - Improvements: Compare time periods with WHERE date BETWEEN
    
    SQL TEMPLATES:
    
    Workout Progress:
    SELECT exercise, DATE(date) as day, MAX(weight) as max_weight
    FROM workouts WHERE exercise = 'deadlift' 
    GROUP BY exercise, DATE(date) ORDER BY day
    
    Cross-Table Insights:
    SELECT DATE(w.date) as day, COUNT(w.id) as workouts, AVG(m.mood_rating) as avg_mood
    FROM workouts w LEFT JOIN mood m ON DATE(w.date) = DATE(m.date)
    GROUP BY DATE(w.date) ORDER BY day
    
    INSIGHT GENERATION:
    - Look for trends, patterns, outliers
    - Compare periods (this week vs last week)
    - Find optimal conditions (best mood → best performance?)
    """
    try:
        sql = arguments['sql']
        format_type = arguments.get('format', 'table')
        
        # Basic SQL injection protection (enhance for production)
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'INSERT', 'UPDATE']
        sql_upper = sql.upper()
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return f"❌ {keyword} operations are not allowed"
        
        # Execute query
        results = db.execute_query(sql)
        
        if not results:
            return "No results found."
        
        if format_type == "json":
            return json.dumps(results, default=str, indent=2)
        
        elif format_type == "summary":
            response = f"## Query Results\n\n"
            response += f"**Rows returned**: {len(results)}\n"
            response += f"**Columns**: {', '.join(results[0].keys())}\n\n"
            
            # Show first few rows
            for i, row in enumerate(results[:5]):
                response += f"**Row {i+1}**: {dict(row)}\n"
            
            if len(results) > 5:
                response += f"\n... and {len(results) - 5} more rows"
            
            return response
        
        else:  # table format
            if not results:
                return "No data found."
            
            # Create markdown table
            headers = list(results[0].keys())
            response = "| " + " | ".join(headers) + " |\n"
            response += "|" + "|".join([" --- "] * len(headers)) + "|\n"
            
            for row in results:
                values = [str(row[header]) if row[header] is not None else "" for header in headers]
                response += "| " + " | ".join(values) + " |\n"
            
            response += f"\n*{len(results)} rows returned*"
            
            return response
        
    except Exception as e:
        return f"❌ Error executing query: {str(e)}"