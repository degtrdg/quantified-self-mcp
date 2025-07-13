"""
Data discovery utilities for quantified self analysis
"""

import glob
import os


def discover_csv_files(data_export_path: str) -> list[str]:
    """
    Dynamically discover all CSV files in the data export directory

    Args:
        data_export_path: Path to the data export directory

    Returns:
        List of CSV filenames (excluding metadata files)
    """
    # Find all CSV files in the export directory
    csv_pattern = os.path.join(data_export_path, "*.csv")
    csv_file_paths = glob.glob(csv_pattern)

    # Filter out metadata files and get just the filenames
    csv_files = []
    for file_path in csv_file_paths:
        filename = os.path.basename(file_path)
        # Skip metadata and other non-data files
        if not filename.startswith("_") and filename != "README.md":
            csv_files.append(filename)

    return csv_files


def load_csv_files(
    data_export_path: str, csv_files: list[str]
) -> list[tuple[str, str]]:
    """
    Load CSV file contents for upload to sandbox

    Args:
        data_export_path: Path to the data export directory
        csv_files: List of CSV filenames to load

    Returns:
        List of tuples (filename, csv_content) for non-empty files
    """
    loaded_files = []

    for csv_file in csv_files:
        try:
            file_path = os.path.join(data_export_path, csv_file)
            with open(file_path, "r") as f:
                csv_data = f.read()
                if csv_data.strip():  # Only include non-empty files
                    loaded_files.append((csv_file, csv_data))
        except FileNotFoundError:
            print(f"Note: {csv_file} not found, skipping...")
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")

    return loaded_files


def get_default_data_path() -> str:
    """Get the default data export path"""
    return "data/export"
