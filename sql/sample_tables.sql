-- Simple SQL tables for quantified self tracking
-- Each table follows consistent patterns: id, date, created_at + domain-specific columns

-- Workouts table
CREATE TABLE workouts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  date TIMESTAMP NOT NULL,
  exercise TEXT NOT NULL,
  sets INTEGER,
  reps INTEGER,
  weight REAL,
  duration_minutes INTEGER,
  calories INTEGER,
  avg_heart_rate INTEGER,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Food/nutrition table
CREATE TABLE food (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  date TIMESTAMP NOT NULL,
  dish_name TEXT,
  protein REAL,
  carbs REAL,
  fats REAL,
  fiber REAL,
  calories INTEGER,
  liked BOOLEAN,
  meal_type TEXT, -- breakfast, lunch, dinner, snack
  created_at TIMESTAMP DEFAULT NOW()
);

-- Sleep tracking table
CREATE TABLE sleep (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  date TIMESTAMP NOT NULL,
  mood_rating INTEGER, -- 1-10 scale
  energy_level INTEGER, -- 1-10 scale
  stress_level INTEGER, -- 1-10 scale
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Sample data
INSERT INTO workouts (date, exercise, sets, reps, weight, notes) VALUES
('2023-06-08 10:30', 'thrusters', 1, 21, 95, '21-15-9 CrossFit WOD'),
('2023-06-08 10:30', 'pullups', 1, 21, NULL, '21-15-9 CrossFit WOD'),
('2023-06-08 10:30', 'thrusters', 2, 15, 95, '21-15-9 CrossFit WOD'),
('2023-06-08 10:30', 'pullups', 2, 15, NULL, '21-15-9 CrossFit WOD'),
('2023-06-08 10:30', 'thrusters', 3, 9, 95, '21-15-9 CrossFit WOD'),
('2023-06-08 10:30', 'pullups', 3, 9, NULL, '21-15-9 CrossFit WOD');

INSERT INTO food (date, dish_name, protein, carbs, fats, fiber, liked) VALUES
('2023-06-08 19:15', 'pasta carbonara', 12, 45, 8, 6, true),
('2023-06-09 12:30', 'chicken salad', 35, 15, 12, 8, true),
('2023-06-09 08:00', 'oatmeal with berries', 8, 45, 6, 12, true);

INSERT INTO sleep (date, bedtime, wake_time, duration_hours, quality_rating) VALUES
('2023-06-08', '2023-06-08 23:30', '2023-06-09 07:00', 7.5, 8),
('2023-06-09', '2023-06-09 23:00', '2023-06-10 06:30', 7.5, 7);

INSERT INTO mood (date, mood_rating, energy_level, stress_level) VALUES
('2023-06-08 09:00', 8, 7, 3),
('2023-06-09 09:00', 7, 8, 4);

-- Common queries for analysis
-- Workout performance over time
SELECT 
  DATE(date) as workout_date,
  exercise,
  MAX(weight) as max_weight,
  SUM(sets * reps) as total_volume
FROM workouts 
WHERE weight IS NOT NULL
GROUP BY DATE(date), exercise
ORDER BY workout_date;

-- Nutrition averages by day
SELECT 
  DATE(date) as day,
  AVG(protein) as avg_protein,
  AVG(carbs) as avg_carbs,
  AVG(fiber) as avg_fiber
FROM food
GROUP BY DATE(date)
ORDER BY day;

-- Correlations between sleep and mood
SELECT 
  s.date,
  s.duration_hours,
  s.quality_rating as sleep_quality,
  m.mood_rating,
  m.energy_level
FROM sleep s
JOIN mood m ON DATE(s.date) = DATE(m.date)
ORDER BY s.date;