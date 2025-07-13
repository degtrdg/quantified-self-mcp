# Quantified Self MCP Demo

This demo showcases the AI learning and metadata system with realistic quantified self data.

## Setup

1. **Seed the database**:
   ```bash
   uv run scripts/seed_demo_data.py
   ```

2. **Start MCP server** (in separate terminal):
   ```bash
   uv run apps/mcp_server/src/server.py
   ```

## Demo Scenarios

### Scenario 1: Discovering Existing Data

**Prompt**: "What data do I have available for tracking?"

**Expected AI Actions**:
1. Use `list_tables()` to see all available tables
2. AI sees tables with metadata and AI learnings
3. Can suggest analyses based on existing data

**Sample Output**:
```markdown
## Available Tables

### workouts
- **Description**: Exercise and strength training sessions  
- **Purpose**: Track workout progress, strength gains, and exercise patterns
- **Columns**: 8
- **AI Insights**: common_exercises, weight_units, typical_rep_ranges

### food
- **Description**: Nutritional intake and meal tracking
- **Purpose**: Monitor nutrition balance, food preferences, and eating patterns  
- **Columns**: 11
- **AI Insights**: macro_nutrients, meal_types, preference_tracking

### sleep
- **Description**: Sleep patterns and quality tracking
- **Purpose**: Analyze sleep quality, duration patterns, and correlation with other metrics
- **Columns**: 8 
- **AI Insights**: quality_scale, optimal_duration, dream_tracking

### mood
- **Description**: Emotional state and energy level tracking
- **Purpose**: Track mood patterns, energy cycles, and stress levels for wellbeing insights
- **Columns**: 6
- **AI Insights**: rating_scales, stress_inverse, daily_variation
```

### Scenario 2: Analyzing Workout Progress

**Prompt**: "Show me my deadlift progress over time"

**Expected AI Actions**:
1. Use `view_table("workouts")` to understand data structure
2. See AI learnings about common exercises and weight units
3. Use `query_data()` with SQL to analyze deadlift progression

**Sample Query**:
```sql
SELECT date, weight, sets, reps, notes
FROM workouts 
WHERE exercise = 'deadlift'
ORDER BY date ASC
```

### Scenario 3: Cross-Domain Analysis

**Prompt**: "How does my sleep quality affect my workout performance?"

**Expected AI Actions**:
1. Use `view_table("sleep")` and `view_table("workouts")` 
2. See AI learnings about sleep quality scales and workout patterns
3. Create JOIN query correlating sleep quality with workout weights

**Sample Query**:
```sql
SELECT 
    s.date,
    s.quality_rating as sleep_quality,
    AVG(w.weight) as avg_workout_weight,
    COUNT(w.id) as workout_count
FROM sleep s
LEFT JOIN workouts w ON DATE(s.date) = DATE(w.date)
WHERE w.weight IS NOT NULL
GROUP BY s.date, s.quality_rating
ORDER BY s.date
```

### Scenario 4: Adding New Data Type

**Prompt**: "I want to start tracking my hydration - water intake throughout the day"

**Expected AI Actions**:
1. Use `list_tables()` to check existing tables
2. Determine hydration doesn't fit existing tables (new domain)
3. Use `create_table()` to create hydration tracking table

**Sample Table Creation**:
```python
create_table(
    table_name="hydration",
    description="Daily water intake tracking",
    purpose="Monitor hydration levels and patterns for health optimization",
    columns=[
        {"name": "amount_ml", "type": "INTEGER", "description": "Water amount in milliliters", "units": "ml", "required": True},
        {"name": "source", "type": "TEXT", "description": "Source of hydration (water, tea, coffee, etc.)"},
        {"name": "temperature", "type": "TEXT", "description": "Hot, cold, or room temperature"}
    ]
)
```

### Scenario 5: Schema Evolution

**Prompt**: "I want to start tracking RPE (Rate of Perceived Exertion) for my workouts"

**Expected AI Actions**:
1. Use `view_table("workouts")` to see current schema
2. Recognize this fits existing workout domain
3. Use `edit_table_schema()` to add RPE column
4. Update AI learnings with new column purpose

**Sample Schema Edit**:
```python
edit_table_schema(
    table_name="workouts",
    operations=[
        {
            "action": "add_column",
            "name": "rpe",
            "type": "INTEGER", 
            "description": "Rate of Perceived Exertion (1-10 scale)"
        }
    ]
)
```

### Scenario 6: Food Preference Analysis

**Prompt**: "What foods do I like most based on my tracking?"

**Expected AI Actions**:
1. Use `view_table("food")` to understand schema
2. See AI learnings about preference tracking (liked field)
3. Query foods with high like ratings

**Sample Query**:
```sql
SELECT 
    dish_name,
    AVG(protein) as avg_protein,
    AVG(calories) as avg_calories,
    COUNT(*) as times_eaten
FROM food 
WHERE liked = true
GROUP BY dish_name
ORDER BY times_eaten DESC, avg_protein DESC
LIMIT 10
```

## AI Learning Evolution

As the demo progresses, the AI learnings grow:

**Initial State** (after seeding):
```json
{
  "common_exercises": ["deadlift", "bench_press", "squat", "overhead_press"],
  "weight_units": "lbs",
  "typical_rep_ranges": "3-10 reps per set"
}
```

**After Adding RPE**:
```json
{
  "common_exercises": ["deadlift", "bench_press", "squat", "overhead_press"],
  "weight_units": "lbs", 
  "typical_rep_ranges": "3-10 reps per set",
  "schema_evolution": {
    "rpe_added": "2024-07-13",
    "reason": "User wants to track perceived exertion for better training insights"
  }
}
```

**After Several Data Insertions**:
```json
{
  "common_exercises": ["deadlift", "bench_press", "squat", "overhead_press"],
  "weight_units": "lbs",
  "typical_rep_ranges": "3-10 reps per set",
  "schema_evolution": {
    "rpe_added": "2024-07-13",
    "reason": "User wants to track perceived exertion for better training insights"
  },
  "insertion_patterns": {
    "recent_data_types": {"exercise": "str", "weight": "float", "rpe": "int"},
    "recent_columns_used": ["exercise", "date", "sets", "reps", "weight", "rpe"],
    "last_insertion": "deadlift session with 315 lbs, RPE 8"
  }
}
```

## Key Demo Points

1. **Metadata Discovery**: AI can understand what data exists and how to use it
2. **Cross-Domain Intelligence**: AI knows relationships between sleep, workouts, mood
3. **Schema Evolution**: Smart decisions about when to extend vs create new tables  
4. **Learning Accumulation**: System gets smarter with each interaction
5. **Context Preservation**: AI remembers user preferences and data patterns

This demo shows how the metadata system transforms a basic MCP server into an intelligent, learning system that improves over time.