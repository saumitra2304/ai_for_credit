import sqlite3

from sql_db.db import DB_PATH, init_db_sync

if __name__ == "__main__":
    init_db_sync()
    print(f"Initialized SQLite database at {DB_PATH}")
