#!/usr/bin/env python3
"""
Comprehensive Data Extraction Script
Pulls data from all databases and JSON files in the workspace
"""

import sqlite3
import json
import os
import glob
from datetime import datetime
import csv

def extract_database_data():
    """Extract data from all SQLite databases"""
    print("=== DATABASE EXTRACTION ===")
    
    # Find all .db files
    db_files = glob.glob('/workspace/**/*.db', recursive=True)
    
    all_data = {}
    
    for db_path in db_files:
        print(f"\nProcessing: {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            db_data = {}
            for table in tables:
                table_name = table[0]
                print(f"  Extracting table: {table_name}")
                
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table_name})")
                schema = cursor.fetchall()
                
                # Get all data
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Get column names
                column_names = [description[0] for description in cursor.description]
                
                db_data[table_name] = {
                    'schema': schema,
                    'columns': column_names,
                    'data': rows,
                    'row_count': len(rows)
                }
                
                print(f"    Rows: {len(rows)}")
            
            all_data[os.path.basename(db_path)] = db_data
            conn.close()
            
        except Exception as e:
            print(f"  Error processing {db_path}: {e}")
    
    return all_data

def extract_json_data():
    """Extract data from JSON files"""
    print("\n=== JSON DATA EXTRACTION ===")
    
    # Find all JSON files
    json_files = glob.glob('/workspace/**/*.json', recursive=True)
    
    all_json_data = {}
    
    for json_path in json_files:
        print(f"Processing: {json_path}")
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Store basic info about the JSON file
            all_json_data[os.path.basename(json_path)] = {
                'path': json_path,
                'size': os.path.getsize(json_path),
                'data_type': type(data).__name__,
                'keys': list(data.keys()) if isinstance(data, dict) else 'Not a dict',
                'data': data
            }
            
            print(f"  Size: {os.path.getsize(json_path)} bytes")
            print(f"  Type: {type(data).__name__}")
            if isinstance(data, dict):
                print(f"  Keys: {list(data.keys())}")
            
        except Exception as e:
            print(f"  Error processing {json_path}: {e}")
    
    return all_json_data

def create_summary_report(db_data, json_data):
    """Create a comprehensive summary report"""
    print("\n=== CREATING SUMMARY REPORT ===")
    
    summary = {
        'extraction_timestamp': datetime.now().isoformat(),
        'databases': {},
        'json_files': {},
        'statistics': {}
    }
    
    # Database summary
    total_db_rows = 0
    for db_name, db_info in db_data.items():
        db_summary = {
            'tables': list(db_info.keys()),
            'total_tables': len(db_info),
            'total_rows': sum(table['row_count'] for table in db_info.values())
        }
        summary['databases'][db_name] = db_summary
        total_db_rows += db_summary['total_rows']
    
    # JSON files summary
    total_json_files = len(json_data)
    total_json_size = sum(file_info['size'] for file_info in json_data.values())
    
    for json_name, json_info in json_data.items():
        summary['json_files'][json_name] = {
            'size': json_info['size'],
            'data_type': json_info['data_type'],
            'keys': json_info['keys']
        }
    
    # Overall statistics
    summary['statistics'] = {
        'total_databases': len(db_data),
        'total_database_rows': total_db_rows,
        'total_json_files': total_json_files,
        'total_json_size_bytes': total_json_size,
        'total_data_sources': len(db_data) + total_json_files
    }
    
    return summary

def export_to_csv(db_data, output_dir='/workspace/extracted_data'):
    """Export database data to CSV files"""
    print(f"\n=== EXPORTING TO CSV ===")
    
    os.makedirs(output_dir, exist_ok=True)
    
    for db_name, db_info in db_data.items():
        db_dir = os.path.join(output_dir, f"database_{db_name.replace('.db', '')}")
        os.makedirs(db_dir, exist_ok=True)
        
        for table_name, table_info in db_info.items():
            if table_info['row_count'] > 0:
                csv_path = os.path.join(db_dir, f"{table_name}.csv")
                
                with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(table_info['columns'])
                    writer.writerows(table_info['data'])
                
                print(f"  Exported {table_info['row_count']} rows to {csv_path}")

def main():
    print("Starting comprehensive data extraction...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Extract data
    db_data = extract_database_data()
    json_data = extract_json_data()
    
    # Create summary
    summary = create_summary_report(db_data, json_data)
    
    # Save summary
    with open('/workspace/data_extraction_summary.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    # Export to CSV
    export_to_csv(db_data)
    
    # Save raw data
    with open('/workspace/extracted_database_data.json', 'w') as f:
        json.dump(db_data, f, indent=2, default=str)
    
    with open('/workspace/extracted_json_data.json', 'w') as f:
        json.dump(json_data, f, indent=2, default=str)
    
    print(f"\n=== EXTRACTION COMPLETE ===")
    print(f"Summary saved to: /workspace/data_extraction_summary.json")
    print(f"Database data saved to: /workspace/extracted_database_data.json")
    print(f"JSON data saved to: /workspace/extracted_json_data.json")
    print(f"CSV files exported to: /workspace/extracted_data/")
    
    # Print summary statistics
    print(f"\n=== SUMMARY STATISTICS ===")
    stats = summary['statistics']
    print(f"Total databases: {stats['total_databases']}")
    print(f"Total database rows: {stats['total_database_rows']}")
    print(f"Total JSON files: {stats['total_json_files']}")
    print(f"Total JSON size: {stats['total_json_size_bytes']:,} bytes")
    print(f"Total data sources: {stats['total_data_sources']}")

if __name__ == "__main__":
    main()