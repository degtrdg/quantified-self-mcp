"""Data Loading Utility for Analysis Agents

Simple utility to load exported CSV data into pandas DataFrames
for analysis agents with code interpreters.
"""

import pandas as pd
import os
from typing import Dict, Any, Optional

class DataLoader:
    """Load exported CSV data for analysis"""
    
    def __init__(self, data_dir: str = "data/export"):
        self.data_dir = data_dir
        self.metadata = None
        self._load_metadata()
    
    def _load_metadata(self):
        """Load metadata about available tables"""
        metadata_path = os.path.join(self.data_dir, "_metadata.csv")
        if os.path.exists(metadata_path):
            self.metadata = pd.read_csv(metadata_path)
        else:
            print(f"⚠️ No metadata found at {metadata_path}")
    
    def list_tables(self) -> pd.DataFrame:
        """Get overview of available tables"""
        if self.metadata is not None:
            return self.metadata
        else:
            return pd.DataFrame()
    
    def load_table(self, table_name: str, parse_dates: bool = True) -> Optional[pd.DataFrame]:
        """Load a specific table"""
        csv_path = os.path.join(self.data_dir, f"{table_name}.csv")
        
        if not os.path.exists(csv_path):
            print(f"❌ Table {table_name} not found at {csv_path}")
            return None
        
        try:
            if parse_dates:
                # Common datetime columns in quantified self data
                date_columns = ['date', 'created_at', 'updated_at', 'bedtime', 'wake_time']
                
                # Only parse columns that actually exist
                df_preview = pd.read_csv(csv_path, nrows=0)
                existing_date_cols = [col for col in date_columns if col in df_preview.columns]
                
                if existing_date_cols:
                    df = pd.read_csv(csv_path, parse_dates=existing_date_cols)
                else:
                    df = pd.read_csv(csv_path)
            else:
                df = pd.read_csv(csv_path)
            
            print(f"✅ Loaded {table_name}: {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            print(f"❌ Error loading {table_name}: {e}")
            return None
    
    def load_all_tables(self, parse_dates: bool = True) -> Dict[str, pd.DataFrame]:
        """Load all available tables"""
        tables = {}
        
        if self.metadata is None:
            print("❌ No metadata available")
            return tables
        
        for _, row in self.metadata.iterrows():
            table_name = row['table_name']
            df = self.load_table(table_name, parse_dates)
            if df is not None:
                tables[table_name] = df
        
        return tables
    
    def get_table_info(self, table_name: str = None) -> str:
        """Get information about a table or all tables"""
        if self.metadata is None:
            return "❌ No metadata available"
        
        if table_name:
            # Info for specific table
            table_row = self.metadata[self.metadata['table_name'] == table_name]
            if table_row.empty:
                return f"❌ Table {table_name} not found"
            
            row = table_row.iloc[0]
            info = f"""
📊 **{table_name}**
• Description: {row['description']}
• Purpose: {row['purpose']}
• Rows: {row['row_count']:,}
• Columns: {row['column_count']}
• Date Range: {row['date_range']}
• Last Updated: {row['last_updated']}
• File: {row['csv_file']}
"""
            return info.strip()
        else:
            # Overview of all tables
            total_rows = self.metadata['row_count'].sum()
            table_count = len(self.metadata)
            
            info = [f"📊 **Data Overview**: {table_count} tables, {total_rows:,} total rows\n"]
            
            for _, row in self.metadata.iterrows():
                info.append(f"• **{row['table_name']}**: {row['row_count']:,} rows - {row['description']}")
            
            return "\n".join(info)

# Convenience functions for quick usage
def quick_load(data_dir: str = "data/export") -> Dict[str, pd.DataFrame]:
    """Quickly load all tables into a dictionary"""
    loader = DataLoader(data_dir)
    return loader.load_all_tables()

def quick_overview(data_dir: str = "data/export") -> str:
    """Get quick overview of available data"""
    loader = DataLoader(data_dir)
    return loader.get_table_info()

# Example usage for analysis agents
if __name__ == "__main__":
    print("🔍 Quantified Self Data Loader")
    print("=" * 40)
    
    # Initialize loader
    loader = DataLoader("data/export_test")  # Update path as needed
    
    # Show overview
    print(loader.get_table_info())
    print()
    
    # Load all data
    print("📊 Loading all tables...")
    tables = loader.load_all_tables()
    
    if tables:
        print("\\n✅ Available DataFrames:")
        for name, df in tables.items():
            print(f"  • {name}: {df.shape}")
            
        print("\\n💡 Example Analysis:")
        
        # Example analysis if workouts data exists
        if 'workouts' in tables and len(tables['workouts']) > 0:
            workouts = tables['workouts']
            print(f"  • Total workouts: {len(workouts)}")
            if 'exercise' in workouts.columns:
                top_exercises = workouts['exercise'].value_counts().head(3)
                print(f"  • Top exercises: {list(top_exercises.index)}")
        
        # Example analysis if food data exists  
        if 'food' in tables and len(tables['food']) > 0:
            food = tables['food']
            print(f"  • Total meals tracked: {len(food)}")
            if 'calories' in food.columns:
                avg_calories = food['calories'].mean()
                print(f"  • Average calories per meal: {avg_calories:.1f}")
    
    else:
        print("❌ No data tables found")