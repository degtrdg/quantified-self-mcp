# MCP Tool Usage Examples

Examples of how the AI uses MCP tools to interact with the SQL database.

## Tool: list_tables

**Purpose**: Discover existing tables and their schemas

**Example Usage**:
```
AI: I need to understand what data is already being tracked.
Tool: list_tables()
Response: {
  "tables": [
    {
      "name": "workouts",
      "description": "Physical exercise tracking",
      "columns": [
        {"name": "id", "type": "UUID", "description": "Primary key"},
        {"name": "date", "type": "TIMESTAMP", "description": "When the workout occurred"},
        {"name": "exercise", "type": "TEXT", "description": "Name of the exercise"},
        {"name": "sets", "type": "INTEGER", "description": "Number of sets"},
        {"name": "reps", "type": "INTEGER", "description": "Repetitions per set"},
        {"name": "weight", "type": "REAL", "description": "Weight used in lbs"}
      ],
      "row_count": 25,
      "recent_data": "Last entry: 2023-06-08 - thrusters, 95 lbs"
    }
  ]
}
```

## Tool: create_table

**Purpose**: Create new table when tracking something completely new

**Example Usage**:
```
User: "I want to start tracking my medication"
AI: I don't see a medications table. Let me create one.
Tool: create_table("medications", {
  "description": "Daily medication tracking",
  "columns": [
    {"name": "date", "type": "TIMESTAMP", "description": "When medication was taken"},
    {"name": "medication_name", "type": "TEXT", "description": "Name of the medication"},
    {"name": "dosage", "type": "TEXT", "description": "Dosage amount (e.g., 10mg)"},
    {"name": "taken", "type": "BOOLEAN", "description": "Whether the medication was taken"},
    {"name": "notes", "type": "TEXT", "description": "Additional notes or side effects"}
  ]
})
```

## Tool: add_column

**Purpose**: Extend existing table with new data fields

**Example Usage**:
```
User: "I want to track RPE (Rate of Perceived Exertion) for my workouts"
AI: I see the workouts table exists, but doesn't have RPE. Let me add that column.
Tool: add_column("workouts", {
  "name": "rpe",
  "type": "INTEGER", 
  "description": "Rate of Perceived Exertion (1-10 scale)"
})
```

## Tool: insert_data

**Purpose**: Store extracted data into appropriate table

**Example Usage**:
```
User: Photo of CrossFit whiteboard showing "5x5 deadlifts at 185 lbs"
AI: I'll store this workout data.
Tool: insert_data("workouts", {
  "date": "2023-06-09 08:30",
  "exercise": "deadlift",
  "sets": 5,
  "reps": 5,
  "weight": 185,
  "notes": "5x5 strength training"
})
```

## Tool: query_data

**Purpose**: Analyze data and find patterns

**Example Usage**:
```
User: "How has my deadlift progressed over the last month?"
AI: Let me analyze your deadlift progression.
Tool: query_data("""
  SELECT 
    date,
    weight,
    sets * reps as total_volume
  FROM workouts 
  WHERE exercise = 'deadlift' 
    AND date >= CURRENT_DATE - INTERVAL '30 days'
  ORDER BY date
""")

Response: Shows progression from 155 lbs to 185 lbs over 4 weeks
```

## Common Workflow Patterns

### Pattern 1: New User, First Data Entry
1. `list_tables()` - see what exists (probably nothing)
2. `create_table()` - create workouts table
3. `insert_data()` - store their first workout

### Pattern 2: Adding New Metric to Existing Data
1. `list_tables()` - see existing workouts table
2. `add_column()` - add RPE column
3. `insert_data()` - store workout with RPE

### Pattern 3: Analysis Request
1. `list_tables()` - understand available data
2. `query_data()` - run analysis SQL
3. Format results for human consumption

### Pattern 4: Ambiguous Input
1. `list_tables()` - see available tables
2. Ask user for clarification
3. Use appropriate tool based on response

## Error Handling

**Column Already Exists**:
```
Tool: add_column("workouts", {"name": "reps", "type": "INTEGER"})
Error: "Column 'reps' already exists"
AI Response: "I see the workouts table already tracks reps. I'll use the existing column."
```

**Invalid Data Type**:
```
Tool: insert_data("workouts", {"weight": "heavy"})
Error: "Invalid data type for weight column (expected REAL)"
AI Response: "I need a numeric weight value. Can you provide the weight in pounds?"
```

**Table Doesn't Exist**:
```
Tool: insert_data("meditation", {...})
Error: "Table 'meditation' does not exist"
AI Response: "I need to create a meditation table first. Let me do that."
→ create_table("meditation", ...)
```