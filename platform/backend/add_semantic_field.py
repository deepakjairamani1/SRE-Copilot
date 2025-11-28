#!/usr/bin/env python3
"""
Add semantic_processing field to incidents table
"""
import sqlite3
import os

def add_semantic_field():
    db_path = "data/sre_copilot.db"
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. Run init_db.py first.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(incidents)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'semantic_processing' not in columns:
            print("Adding semantic_processing column to incidents table...")
            cursor.execute("ALTER TABLE incidents ADD COLUMN semantic_processing TEXT")
            conn.commit()
            print("✓ semantic_processing column added successfully")
        else:
            print("✓ semantic_processing column already exists")
        
        conn.close()
        
    except Exception as e:
        print(f"Error adding semantic_processing field: {e}")

if __name__ == "__main__":
    add_semantic_field()