
#!/usr/bin/env python3
"""
Script to clean CSV files by removing 'sep=,' lines and other formatting issues.
"""

import os
import glob

def clean_csv_file(file_path):
    """Clean a single CSV file by removing problematic lines."""
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Filter out problematic lines
        cleaned_lines = []
        for line in lines:
            # Skip lines that start with 'sep='
            if line.strip().startswith('sep='):
                print(f"  Removed line: {line.strip()}")
                continue
            # Skip empty lines
            if line.strip() == '':
                continue
            cleaned_lines.append(line)
        
        # Write the cleaned file back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
        
        print(f"✅ Cleaned {file_path} - removed {len(lines) - len(cleaned_lines)} problematic lines")
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning {file_path}: {e}")
        return False

def main():
    """Clean all CSV files in the data directory."""
    print("🧹 Cleaning CSV files in data directory...")
    
    # Find all CSV files in the data directory
    csv_files = glob.glob("data/*.csv")
    
    if not csv_files:
        print("No CSV files found in data directory")
        return
    
    print(f"Found {len(csv_files)} CSV files to clean:")
    
    cleaned_count = 0
    for csv_file in csv_files:
        print(f"\nCleaning: {csv_file}")
        if clean_csv_file(csv_file):
            cleaned_count += 1
    
    print(f"\n🎯 Summary: Successfully cleaned {cleaned_count}/{len(csv_files)} CSV files")
    print("You can now run the main script again to process all ship tracks!")

if __name__ == "__main__":
    main()
