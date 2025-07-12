# Supabase Setup Guide

Complete setup instructions for PostgreSQL database with Supabase.

## 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create account
2. Create new project: "quantified-self-mcp"
3. Choose region closest to you
4. Generate secure password and save it

## 2. Database Setup

### Initial Tables
Run these SQL commands in Supabase SQL Editor:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Workouts table
CREATE TABLE workouts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  date TIMESTAMP NOT NULL,
  exercise TEXT NOT NULL,
  sets INTEGER,
  reps INTEGER,
  weight REAL,
  duration_minutes INTEGER,
  calories INTEGER,
  avg_heart_rate INTEGER,
  rpe INTEGER, -- Rate of Perceived Exertion (1-10)
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Food/nutrition table
CREATE TABLE food (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  date TIMESTAMP NOT NULL,
  dish_name TEXT,
  protein REAL,
  carbs REAL,
  fats REAL,
  fiber REAL,
  calories INTEGER,
  liked BOOLEAN,
  meal_type TEXT, -- breakfast, lunch, dinner, snack
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Sleep tracking table
CREATE TABLE sleep (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  date TIMESTAMP NOT NULL, -- date of the sleep (bedtime date)
  bedtime TIMESTAMP,
  wake_time TIMESTAMP,
  duration_hours REAL,
  quality_rating INTEGER, -- 1-10 scale
  dream_recall BOOLEAN,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Mood/wellness table
CREATE TABLE mood (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  date TIMESTAMP NOT NULL,
  mood_rating INTEGER, -- 1-10 scale
  energy_level INTEGER, -- 1-10 scale
  stress_level INTEGER, -- 1-10 scale
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Table metadata for MCP tools
CREATE TABLE table_metadata (
  table_name TEXT PRIMARY KEY,
  description TEXT NOT NULL,
  purpose TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Column metadata for MCP tools
CREATE TABLE column_metadata (
  table_name TEXT,
  column_name TEXT,
  description TEXT,
  data_type TEXT,
  units TEXT,
  constraints TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (table_name, column_name)
);
```

### Metadata Setup
```sql
-- Insert table metadata
INSERT INTO table_metadata (table_name, description, purpose) VALUES
('workouts', 'Physical exercise and training sessions', 'Track workout performance and progression'),
('food', 'Nutritional intake and meal information', 'Monitor diet and nutritional habits'),
('sleep', 'Sleep patterns and quality metrics', 'Analyze sleep health and patterns'),
('mood', 'Daily mood and wellness tracking', 'Monitor mental health and energy levels');

-- Insert column metadata for workouts
INSERT INTO column_metadata (table_name, column_name, description, data_type, units) VALUES
('workouts', 'date', 'When the workout occurred', 'TIMESTAMP', NULL),
('workouts', 'exercise', 'Name of the exercise performed', 'TEXT', NULL),
('workouts', 'sets', 'Number of sets completed', 'INTEGER', 'count'),
('workouts', 'reps', 'Repetitions per set', 'INTEGER', 'count'),
('workouts', 'weight', 'Weight used for the exercise', 'REAL', 'lbs'),
('workouts', 'duration_minutes', 'Total workout duration', 'INTEGER', 'minutes'),
('workouts', 'calories', 'Estimated calories burned', 'INTEGER', 'kcal'),
('workouts', 'avg_heart_rate', 'Average heart rate during workout', 'INTEGER', 'bpm'),
('workouts', 'rpe', 'Rate of Perceived Exertion', 'INTEGER', 'scale_1_10'),
('workouts', 'notes', 'Additional workout notes', 'TEXT', NULL);

-- Insert column metadata for food
INSERT INTO column_metadata (table_name, column_name, description, data_type, units) VALUES
('food', 'date', 'When the food was consumed', 'TIMESTAMP', NULL),
('food', 'dish_name', 'Name or description of the food/dish', 'TEXT', NULL),
('food', 'protein', 'Protein content', 'REAL', 'grams'),
('food', 'carbs', 'Carbohydrate content', 'REAL', 'grams'),
('food', 'fats', 'Fat content', 'REAL', 'grams'),
('food', 'fiber', 'Fiber content', 'REAL', 'grams'),
('food', 'calories', 'Caloric content', 'INTEGER', 'kcal'),
('food', 'liked', 'Whether the user enjoyed the food', 'BOOLEAN', NULL),
('food', 'meal_type', 'Type of meal (breakfast, lunch, dinner, snack)', 'TEXT', NULL);
```

## 3. Connection Configuration

### Get Connection Details
1. Go to Project Settings → Database
2. Copy these values:
   - Host
   - Database name  
   - Port (usually 5432)
   - User (postgres)
   - Password (the one you set)

### Environment Variables
Create `.env` file:
```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Database Connection
DATABASE_URL=postgresql://postgres:your-password@db.your-project.supabase.co:5432/postgres

# For direct connection
DB_HOST=db.your-project.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-password
```

## 4. Row Level Security (RLS)

Enable RLS for production:
```sql
-- Enable RLS on all tables
ALTER TABLE workouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE food ENABLE ROW LEVEL SECURITY;
ALTER TABLE sleep ENABLE ROW LEVEL SECURITY;
ALTER TABLE mood ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust based on your auth needs)
CREATE POLICY "Users can access their own data" ON workouts
  FOR ALL USING (true); -- Adjust for your auth system

-- Repeat for other tables
```

## 5. Test Connection

Test with psql or your preferred SQL client:
```bash
psql "postgresql://postgres:your-password@db.your-project.supabase.co:5432/postgres"
```

Or test with Python:
```python
import psycopg2
import os

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
print(cur.fetchall())
```

## 6. Sample Data (Optional)

Insert test data:
```sql
-- Sample workout data
INSERT INTO workouts (date, exercise, sets, reps, weight, notes) VALUES
('2023-06-08 10:30', 'deadlift', 3, 5, 185, 'Felt strong today'),
('2023-06-08 10:45', 'bench_press', 3, 8, 135, 'Good form'),
('2023-06-09 08:30', 'squat', 4, 6, 155, 'New PR!');

-- Sample food data
INSERT INTO food (date, dish_name, protein, carbs, fats, liked) VALUES
('2023-06-08 12:30', 'chicken salad', 35, 15, 12, true),
('2023-06-08 19:15', 'pasta with marinara', 12, 45, 8, true);
```

Your Supabase database is now ready for the MCP server!