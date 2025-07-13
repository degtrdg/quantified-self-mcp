"""CSV Export Utility for Quantified Self Data

Simple utility to export all tables and metadata to CSV files for analysis agents.
Perfect for passing data to pandas-based analysis workflows.
"""

import csv
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

# Add path for database helpers
sys.path.append(os.path.dirname(__file__))
from database_helpers import db_helper


class CSVExporter:
    """Export all database tables and metadata to CSV files"""

    def __init__(self, output_dir: str = "data/export"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Ensure fresh database connection
        if db_helper.connection:
            db_helper.connection.rollback()  # Clear any failed transactions

    def export_all_tables(self) -> Dict[str, str]:
        """Export all data tables to CSV files and create metadata summary"""

        print("🔄 Starting CSV export...")

        # Get all data tables (excluding metadata tables)
        tables = self._get_data_tables()

        results = {}
        table_info = []

        for table_name in tables:
            print(f"📊 Exporting {table_name}...")

            # Export table data
            csv_path = self._export_table_data(table_name)

            # Get table metadata
            metadata = self._get_table_metadata(table_name)

            # Get table stats
            stats = self._get_table_stats(table_name)

            results[table_name] = csv_path

            table_info.append(
                {
                    "table_name": table_name,
                    "csv_file": os.path.basename(csv_path),
                    "description": metadata.get("description", ""),
                    "purpose": metadata.get("purpose", ""),
                    "row_count": stats["row_count"],
                    "column_count": stats["column_count"],
                    "date_range": stats.get("date_range", ""),
                    "last_updated": stats.get("last_updated", ""),
                }
            )

        # Create metadata summary file
        metadata_path = self._create_metadata_summary(table_info)
        results["_metadata"] = metadata_path

        print(f"✅ Export complete! {len(tables)} tables exported to {self.output_dir}")
        return results

    def _get_data_tables(self) -> List[str]:
        """Get list of data tables (excluding metadata tables)"""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND table_name NOT LIKE '%_metadata'
        ORDER BY table_name
        """

        tables = db_helper.execute_query(query)
        return [table["table_name"] for table in tables]

    def _export_table_data(self, table_name: str) -> str:
        """Export a single table's data to CSV"""

        # Get all data from table
        data = db_helper.execute_query(
            f"SELECT * FROM {table_name} ORDER BY created_at DESC"
        )

        # Create CSV file
        csv_filename = f"{table_name}.csv"
        csv_path = os.path.join(self.output_dir, csv_filename)

        if data:
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                # Handle datetime serialization
                for row in data:
                    serialized_row = {}
                    for key, value in row.items():
                        if isinstance(value, datetime):
                            serialized_row[key] = value.isoformat()
                        else:
                            serialized_row[key] = value
                    writer.writerow(serialized_row)
        else:
            # Create empty CSV with just headers
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                # Get column names from schema
                schema = db_helper.execute_query(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' AND table_schema = 'public'
                    ORDER BY ordinal_position
                """)

                if schema:
                    fieldnames = [col["column_name"] for col in schema]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()

        return csv_path

    def _get_table_metadata(self, table_name: str) -> Dict[str, str]:
        """Get table metadata from table_metadata table"""

        query = """
        SELECT description, purpose, created_at, updated_at
        FROM table_metadata 
        WHERE table_name = %s
        """

        result = db_helper.execute_query(query, (table_name,))

        if result:
            metadata = result[0]
            return {
                "description": metadata["description"] or "",
                "purpose": metadata["purpose"] or "",
                "created_at": metadata["created_at"].isoformat()
                if metadata["created_at"]
                else "",
                "updated_at": metadata["updated_at"].isoformat()
                if metadata["updated_at"]
                else "",
            }

        return {"description": "", "purpose": "", "created_at": "", "updated_at": ""}

    def _get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Get table statistics"""

        # Get row count
        count_result = db_helper.execute_query(
            f"SELECT COUNT(*) as count FROM {table_name}"
        )
        row_count = count_result[0]["count"] if count_result else 0

        # Get column count
        column_result = db_helper.execute_query(f"""
            SELECT COUNT(*) as count 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' AND table_schema = 'public'
        """)
        column_count = column_result[0]["count"] if column_result else 0

        stats = {"row_count": row_count, "column_count": column_count}

        # Try to get date range if there's a date column
        try:
            # First check if date column exists
            has_date = db_helper.execute_query(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND column_name = 'date' 
                AND table_schema = 'public'
            """)

            if has_date:
                date_range_result = db_helper.execute_query(f"""
                    SELECT 
                        MIN(date) as earliest_date,
                        MAX(date) as latest_date
                    FROM {table_name}
                    WHERE date IS NOT NULL
                """)

                if date_range_result and date_range_result[0]["earliest_date"]:
                    earliest = date_range_result[0]["earliest_date"]
                    latest = date_range_result[0]["latest_date"]

                    if isinstance(earliest, datetime):
                        earliest = earliest.date()
                    if isinstance(latest, datetime):
                        latest = latest.date()

                    stats["date_range"] = f"{earliest} to {latest}"
                else:
                    stats["date_range"] = ""
            else:
                stats["date_range"] = ""
        except Exception as e:
            print(f"  Warning: Could not get date range for {table_name}: {e}")
            stats["date_range"] = ""

        # Try to get last updated timestamp
        try:
            updated_result = db_helper.execute_query(f"""
                SELECT MAX(created_at) as last_updated
                FROM {table_name}
                WHERE created_at IS NOT NULL
            """)

            if updated_result and updated_result[0]["last_updated"]:
                last_updated = updated_result[0]["last_updated"]
                if isinstance(last_updated, datetime):
                    stats["last_updated"] = last_updated.isoformat()
                else:
                    stats["last_updated"] = str(last_updated)
            else:
                stats["last_updated"] = ""
        except:
            stats["last_updated"] = ""

        return stats

    def _create_metadata_summary(self, table_info: List[Dict]) -> str:
        """Create a metadata summary CSV file"""

        metadata_path = os.path.join(self.output_dir, "_metadata.csv")

        with open(metadata_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "table_name",
                "csv_file",
                "description",
                "purpose",
                "row_count",
                "column_count",
                "date_range",
                "last_updated",
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(table_info)

        return metadata_path

    def create_analysis_readme(self) -> str:
        """Create a comprehensive README file for the analysis agent"""

        readme_path = os.path.join(self.output_dir, "README.md")

        # Get export info and metadata
        tables = self._get_data_tables()

        # Load metadata to get actual stats
        metadata_summary = []
        total_rows = 0
        date_ranges = []

        for table_name in tables:
            metadata = self._get_table_metadata(table_name)
            stats = self._get_table_stats(table_name)
            total_rows += stats["row_count"]

            if stats.get("date_range"):
                date_ranges.append(stats["date_range"])

            metadata_summary.append(
                {
                    "name": table_name,
                    "description": metadata["description"],
                    "purpose": metadata["purpose"],
                    "rows": stats["row_count"],
                    "columns": stats["column_count"],
                    "date_range": stats.get("date_range", "N/A"),
                }
            )

        # Determine overall date range
        if date_ranges:
            # Extract earliest and latest dates
            all_dates = []
            for range_str in date_ranges:
                if " to " in range_str:
                    start, end = range_str.split(" to ")
                    all_dates.extend([start.strip(), end.strip()])

            if all_dates:
                overall_range = f"{min(all_dates)} to {max(all_dates)}"
            else:
                overall_range = "Various dates"
        else:
            overall_range = "No date data"

        readme_content = f"""# 📊 Quantified Self Data Export

## 🎯 Overview
This directory contains **{len(tables)} data tables** with **{total_rows:,} total records** from a quantified self tracking system.

**Export Details:**
- 📅 **Generated**: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
- 📈 **Date Range**: {overall_range}
- 🔧 **Format**: CSV files with ISO datetime formatting
- 🐍 **Ready for**: Pandas analysis workflows

## 📋 Data Tables Summary

| Table | Description | Rows | Date Range | Purpose |
|-------|-------------|------|------------|---------|"""

        for table in metadata_summary:
            purpose_short = (
                table["purpose"][:50] + "..."
                if len(table["purpose"]) > 50
                else table["purpose"]
            )
            readme_content += f"\n| **{table['name']}** | {table['description']} | {table['rows']:,} | {table['date_range']} | {purpose_short} |"

        readme_content += f"""

## 📁 Files Structure

### 🏋️ Data Files
"""

        # Add detailed file descriptions with schema info
        for table_name in tables:
            metadata = self._get_table_metadata(table_name)
            stats = self._get_table_stats(table_name)

            # Get sample of actual columns
            try:
                sample_data = db_helper.execute_query(
                    f"SELECT * FROM {table_name} LIMIT 1"
                )
                if sample_data:
                    columns = list(sample_data[0].keys())
                    schema_preview = ", ".join(columns[:6])
                    if len(columns) > 6:
                        schema_preview += f", ... ({len(columns)} total)"
                else:
                    # Get from schema if no data
                    schema_result = db_helper.execute_query(f"""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = '{table_name}' AND table_schema = 'public'
                        ORDER BY ordinal_position
                    """)
                    columns = (
                        [row["column_name"] for row in schema_result]
                        if schema_result
                        else []
                    )
                    schema_preview = ", ".join(columns[:6])
                    if len(columns) > 6:
                        schema_preview += f", ... ({len(columns)} total)"
            except Exception:
                schema_preview = "Schema info unavailable"

            readme_content += f"""
#### 📄 `{table_name}.csv`
**{metadata["description"]}**
- 📊 **{stats["row_count"]:,} rows** × **{stats["column_count"]} columns**
- 🎯 **Purpose**: {metadata["purpose"]}
- 📅 **Date Range**: {stats.get("date_range", "N/A")}
- 🏗️ **Schema**: {schema_preview}
"""

        readme_content += """
### 📋 Meta Files
- **`_metadata.csv`** - Complete table summary with row counts, descriptions, and date ranges
- **`README.md`** - This documentation file

## 🐍 Quick Start with Pandas

### Basic Loading
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load metadata to explore available data
metadata = pd.read_csv('_metadata.csv')
print("Available tables:")
print(metadata[['table_name', 'row_count', 'description']])
```

### Load Specific Tables
```python
# Load tables with automatic datetime parsing
"""

        # Add specific loading examples based on actual data
        if any(table["rows"] > 0 for table in metadata_summary):
            readme_content += """
# Load tables with data
"""
            for table in metadata_summary:
                if table["rows"] > 0:
                    readme_content += f"""
{table["name"]} = pd.read_csv('{table["name"]}.csv', parse_dates=['date', 'created_at'])
print(f"📊 {table["name"].title()}: {{len({table["name"]})}} records")"""

        readme_content += """
```

### Data Exploration Examples
```python
# Quick data overview
for table_name in ['workouts', 'food', 'sleep']:
    try:
        df = pd.read_csv(f'{table_name}.csv', parse_dates=['date', 'created_at'])
        if len(df) > 0:
            print(f"\\n📈 {table_name.title()} Summary:")
            print(f"  • Records: {len(df):,}")
            print(f"  • Date range: {df['date'].min().date()} to {df['date'].max().date()}")
            print(f"  • Columns: {', '.join(df.columns[:5])}...")
    except FileNotFoundError:
        print(f"⚠️  {table_name}.csv not found")
```

## 🔍 Analysis Ideas & Patterns

### 🏋️ Workout Analysis
```python
# Load workout data
workouts = pd.read_csv('workouts.csv', parse_dates=['date', 'created_at'])

if len(workouts) > 0:
    # Exercise frequency
    exercise_counts = workouts['exercise'].value_counts()
    
    # Strength progression (if weight data exists)
    if 'weight' in workouts.columns:
        strength_progress = workouts.groupby('exercise')['weight'].agg(['mean', 'max', 'count'])
    
    # Volume over time
    workouts['volume'] = workouts['sets'] * workouts['reps'] * workouts['weight'].fillna(1)
    weekly_volume = workouts.groupby(pd.Grouper(key='date', freq='W'))['volume'].sum()
```

### 🍎 Nutrition Analysis  
```python
# Load food data
food = pd.read_csv('food.csv', parse_dates=['date', 'created_at'])

if len(food) > 0:
    # Daily nutrition
    daily_nutrition = food.groupby(food['date'].dt.date).agg({
        'estimated_calories': 'sum',
        'protein_grams': 'sum',
        'carbs_grams': 'sum',
        'fat_grams': 'sum'
    })
    
    # Meal patterns
    meal_distribution = food['meal_type'].value_counts()
    
    # Feeling analysis (if available)
    if 'feeling_after' in food.columns:
        feeling_patterns = food['feeling_after'].value_counts()
```

### 😴 Sleep Analysis
```python
# Load sleep data  
sleep = pd.read_csv('sleep.csv', parse_dates=['date', 'created_at'])

if len(sleep) > 0:
    # Sleep duration trends
    sleep['duration_hours'] = pd.to_numeric(sleep['duration_hours'], errors='coerce')
    avg_sleep = sleep['duration_hours'].mean()
    
    # Sleep quality over time
    if 'quality_rating' in sleep.columns:
        sleep_quality_trend = sleep.set_index('date')['quality_rating'].rolling('7D').mean()
```

### 🔗 Cross-Domain Correlations
```python
# Combine datasets for correlation analysis
# Example: Sleep quality vs workout performance
if len(sleep) > 0 and len(workouts) > 0:
    # Merge on date
    daily_sleep = sleep.groupby(sleep['date'].dt.date).agg({
        'duration_hours': 'mean',
        'quality_rating': 'mean'
    })
    
    daily_workouts = workouts.groupby(workouts['date'].dt.date).agg({
        'weight': 'mean',
        'volume': 'sum'
    })
    
    combined = daily_sleep.join(daily_workouts, how='inner')
    correlation = combined.corr()
```

## 📊 Visualization Examples
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Workout progression
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Exercise frequency
workouts['exercise'].value_counts().plot(kind='bar', ax=axes[0,0])
axes[0,0].set_title('Exercise Frequency')

# Nutrition trends  
daily_nutrition['estimated_calories'].plot(ax=axes[0,1])
axes[0,1].set_title('Daily Calories Over Time')

# Sleep quality
if len(sleep) > 0:
    sleep.set_index('date')['quality_rating'].plot(ax=axes[1,0])
    axes[1,0].set_title('Sleep Quality Trends')

plt.tight_layout()
plt.show()
```

## 📚 Data Dictionary

### 🔄 Common Columns
- **`id`**: Unique UUID identifier for each record
- **`date`**: When the event/measurement occurred (ISO datetime)
- **`created_at`**: When the record was entered into database (ISO datetime)

### 🏋️ Workout Columns
- **`exercise`**: Type of exercise performed
- **`sets`**: Number of sets completed  
- **`reps`**: Repetitions per set
- **`weight`**: Weight used (in lbs/kg)
- **`rpe`**: Rate of Perceived Exertion (1-10 scale)

### 🍎 Food Columns
- **`dish_name`**: Name/description of the meal
- **`meal_type`**: Breakfast, lunch, dinner, snack, etc.
- **`ingredients`**: List of ingredients
- **`estimated_calories`**: Caloric content
- **`protein_grams`**: Protein content in grams
- **`carbs_grams`**: Carbohydrate content in grams  
- **`fat_grams`**: Fat content in grams
- **`feeling_after`**: How you felt after eating

### 😴 Sleep Columns
- **`bedtime`**: When you went to bed
- **`wake_time`**: When you woke up
- **`duration_hours`**: Total sleep duration
- **`quality_rating`**: Subjective sleep quality (1-10 scale)
- **`dream_recall`**: Whether you remembered dreams
- **`notes`**: Additional sleep notes

## ⚠️ Data Quality Notes

### Missing Data
- **Empty tables**: Some tables may have 0 rows if no data was tracked yet
- **Null values**: Optional fields may contain null/empty values
- **Date gaps**: Not all dates may have data (tracking isn't necessarily daily)

### Data Types
- **Datetimes**: All in ISO format (YYYY-MM-DDTHH:MM:SS)
- **Numbers**: Weights, calories, ratings are numeric (may have decimals)
- **Text**: Exercise names, ingredients, notes are free-form text

### Recommendations
1. **Always check for null values** before analysis
2. **Use `parse_dates`** when loading CSVs for proper datetime handling
3. **Aggregate by day/week** for trend analysis to handle missing days
4. **Validate numeric ranges** (e.g., calories > 0, sleep hours 0-24)

## 🚀 Advanced Analysis Ideas

1. **Habit Tracking**: Identify patterns in workout consistency, meal timing
2. **Performance Optimization**: Correlate sleep/nutrition with workout performance  
3. **Health Trends**: Track long-term changes in key metrics
4. **Predictive Modeling**: Use historical data to predict future patterns
5. **Behavioral Insights**: Analyze what factors lead to better outcomes

---

💡 **Happy Analyzing!** This data represents real quantified self tracking - explore, visualize, and discover insights!
"""

        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        return readme_path


def export_all_data(output_dir: str = "data/export") -> Dict[str, str]:
    """Convenience function to export all data"""
    exporter = CSVExporter(output_dir)
    results = exporter.export_all_tables()
    readme_path = exporter.create_analysis_readme()
    results["_readme"] = readme_path
    return results


def main():
    """Command line interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Export quantified self data to CSV")
    parser.add_argument(
        "--output", "-o", default="data/export", help="Output directory for CSV files"
    )

    args = parser.parse_args()

    print("🚀 Quantified Self CSV Exporter")
    print(f"📁 Output directory: {args.output}")

    try:
        results = export_all_data(args.output)

        print("\n📊 Export Summary:")
        for name, path in results.items():
            if name.startswith("_"):
                print(f"  📋 {name[1:].title()}: {os.path.basename(path)}")
            else:
                # Get row count from the CSV
                try:
                    with open(path, "r") as f:
                        row_count = sum(1 for line in f) - 1  # Subtract header
                    print(f"  📈 {name}: {row_count} rows → {os.path.basename(path)}")
                except Exception:
                    print(f"  📈 {name}: → {os.path.basename(path)}")

        print(f"\n✅ All data exported to: {args.output}")
        print("🎯 Ready for analysis agent with pandas!")

    except Exception as e:
        print(f"❌ Export failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
