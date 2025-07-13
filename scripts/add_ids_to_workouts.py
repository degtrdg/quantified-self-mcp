#!/usr/bin/env python3
"""
Add UUID IDs to workouts.csv
"""
import csv
import uuid
from pathlib import Path

def add_ids_to_workouts():
    input_file = Path(__file__).parent.parent / "demo" / "seed" / "workouts.csv"
    output_file = input_file
    
    # Read existing data
    rows = []
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Generate UUID for each row
            row['id'] = str(uuid.uuid4())
            rows.append(row)
    
    # Write back with id column first
    with open(output_file, 'w', newline='') as f:
        fieldnames = ['id', 'exercise', 'date', 'sets', 'reps', 'weight', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Added UUIDs to {len(rows)} workout records")

if __name__ == "__main__":
    add_ids_to_workouts()