import sqlite3

def create_database():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    
    # Create users table
    cur.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        department TEXT NOT NULL,
        income REAL NOT NULL,
        experience REAL NOT NULL
    )
    ''')

    # Create rules table
    cur.execute('''
    CREATE TABLE rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        condition TEXT NOT NULL
    )
    ''')
    
    # Insert sample data into users table
    users = [
        ('Alice', 25, 'HR', 55000, 7),
        ('Bob', 30, 'IT', 70000, 12),
        ('Carol', 22, 'Finance', 48000, 5),
        ('Becky', 31, 'Sales', 48000,6),

    ]
    cur.executemany('INSERT INTO users (name, age, department, income, experience) VALUES (?, ?, ?, ?, ?)', users)

    # Insert sample data into rules table
    rules = [
        ('Rule 1', "((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience > 5)"),
        ('Rule 2', "(age > 30 AND department = 'Marketing') AND (salary > 20000 OR experience > 5)"),
    ]
    cur.executemany('INSERT INTO rules (name, condition) VALUES (?, ?)', rules)

    conn.commit()
    conn.close()
    print("Database created and tables initialized successfully.")

if __name__ == "__main__":
    create_database()
