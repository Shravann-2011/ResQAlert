import sqlite3
import os

def setup_database():
    """Initialize the database with required tables"""
    
    # Create database directory if it doesn't exist
    db_dir = 'database'
    os.makedirs(db_dir, exist_ok=True)
    
    db_path = os.path.join(db_dir, 'users.db')
    
    # Remove corrupted database if it exists
    if os.path.exists(db_path):
        try:
            # Test if it's a valid database
            test_conn = sqlite3.connect(db_path)
            test_conn.execute("SELECT 1")
            test_conn.close()
            print(f"✅ Existing database at {db_path} is valid")
        except sqlite3.DatabaseError:
            print(f"⚠️  Corrupted database found at {db_path}, removing...")
            os.remove(db_path)
    
    # Connect to database (creates new one if removed/doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    
    # Verify table was created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone():
        print("✅ Users table created successfully!")
        
        # Show table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\n📋 Table structure:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
    else:
        print("❌ Failed to create users table")
    
    conn.close()
    print(f"\n✅ Database setup complete at: {os.path.abspath(db_path)}")

if __name__ == '__main__':
    setup_database()
