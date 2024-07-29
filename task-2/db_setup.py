import sqlite3

def setup_database():
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    
    # Create table with additional fields for average, min, and max temperature
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        temp REAL NOT NULL,
        feels_like REAL NOT NULL,
        main TEXT NOT NULL,
        dt INTEGER NOT NULL,
        avg_temp REAL,
        min_temp REAL,
        max_temp REAL
    )
    ''')
    
    conn.commit()
    print("Database Created or Updated Successfully")
    return conn, cursor

if __name__ == "__main__":
    setup_database()
