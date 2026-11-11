
import sqlite3
from pathlib import Path

# Database location
BASE_DIR = Path(__file__).resolve().parent
DB_FOLDER = BASE_DIR / "database"
DB_PATH = DB_FOLDER / "it_assets.db"


def get_connection():
    DB_FOLDER.mkdir(exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    # Enable foreign key relationships
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    # 1. USERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Employee',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. ASSETS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            tag TEXT UNIQUE NOT NULL,
            serial TEXT UNIQUE,
            category TEXT NOT NULL,
            assigned_to INTEGER,
            status TEXT NOT NULL DEFAULT 'Available',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (assigned_to)
                REFERENCES users(id)
                ON DELETE SET NULL
        )
    """)

    # 3. TICKETS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            reported_by INTEGER,
            priority TEXT NOT NULL DEFAULT 'Medium',
            status TEXT NOT NULL DEFAULT 'Open',
            date_raised TEXT NOT NULL,
            resolution_notes TEXT,
            date_resolved TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (reported_by)
                REFERENCES users(id)
                ON DELETE SET NULL
        )
    """)

    connection.commit()
    connection.close()

    print("Database created successfully!")
    print("Users, Assets and Tickets tables are ready.")


if __name__ == "__main__":
    create_tables()

    print(f"Database location: {DB_PATH}")
