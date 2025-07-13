# User Flow Analysis - Confirm-Before-Insert Pattern

Core user flows with confirmation step before data insertion.

## Primary User Flow

### **Standard Data Entry Flow**
**Input**: Any quantified self data (photo, text, voice)

**Required Flow**:
1. **Input Agent** → extracts structured data from user input
2. **Extraction Agent** → `list_tables()` to see existing schemas
3. **Extraction Agent** → picks appropriate table (or creates new one)
4. **Extraction Agent** → views schema + recent examples for context
5. **Extraction Agent** → structures input data into table format
6. **Show user preview table** → "Does this look right?"
7. **User confirms** → proceed with insertion
8. **Extraction Agent** → `insert_data()` (single or batch)

## Core Scenarios

### **Scenario 1: CrossFit Workout**
**Input**: Photo "21-15-9 Thrusters 95#, Pull-ups"

**Flow**:
1. Input Agent extracts: workout_type, exercises, rep_scheme, weights
2. Extraction Agent sees workouts table, views recent entries
3. **Presents preview table to user:**
   ```
   | date | exercise | set | reps | weight | notes |
   |------|----------|-----|------|--------|-------|
   | 2023-06-08 | thrusters | 1 | 21 | 95 | 21-15-9 WOD |
   | 2023-06-08 | pullups | 1 | 21 | bodyweight | 21-15-9 WOD |
   | 2023-06-08 | thrusters | 2 | 15 | 95 | 21-15-9 WOD |
   | ... | ... | ... | ... | ... | ... |
   ```
4. User confirms: "Yes, looks good"
5. `insert_data()` with batch of 6 rows

### **Scenario 2: New Data Type**
**Input**: "Track my meditation - 20 minutes, focused breathing"

**Flow**:
1. Input Agent extracts: activity_type, duration, technique
2. Extraction Agent sees no meditation table
3. **Presents preview to user:**
   ```
   New table: meditation
   | date | duration_minutes | technique | focus_rating |
   |------|------------------|-----------|--------------|
   | 2023-06-08 | 20 | focused_breathing | null |
   ```
4. User confirms: "Yes, create this table"
5. `create_table()` + `insert_data()`

## Key Improvements Needed

### **1. Versatile insert_data Tool**
Current: Only handles single rows
**Updated**: Handle both single rows and arrays of rows

```python
# Single row
insert_data("workouts", {"date": "...", "exercise": "..."})

# Batch rows  
insert_data("workouts", [
  {"date": "...", "exercise": "thrusters", "set": 1},
  {"date": "...", "exercise": "thrusters", "set": 2},
  {"date": "...", "exercise": "pullups", "set": 1}
])
```

### **2. Preview/Confirmation Step**
- Extraction Agent formats data into readable table
- Shows user exactly what will be inserted
- Waits for confirmation before proceeding
- Handles user corrections/modifications

### **3. Context-Aware Schema Selection**
- `list_tables()` shows recent examples from each table
- AI uses examples to understand expected data format
- Consistent with existing patterns

## Testing Scenarios

### **Test 1: Multi-Exercise Workout**
Input: "Deadlift 3x5 at 185, then bench 3x8 at 135"
Expected: Preview table with 6 rows, user confirms, batch insert

### **Test 2: Schema Evolution**
Input: "Same workout but track RPE this time"  
Expected: Add RPE column, preview shows new field, batch insert

### **Test 3: New Domain**
Input: "Started taking vitamin D, 2000 IU daily"
Expected: Create supplements table, preview schema, confirm and insert