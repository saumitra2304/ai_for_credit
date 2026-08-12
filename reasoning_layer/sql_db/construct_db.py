import sqlite3
from dotenv import load_dotenv

load_dotenv()
conn = sqlite3.connect("./credit_ai_db.db")

conn.execute("PRAGMA journal_mode = WAL;")

cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS user_features (
        user_id       BIGINT  NOT NULL,
        cin           TEXT    NOT NULL,
        brisk         BOOLEAN,
        insta_summary BOOLEAN,
        credit        BOOLEAN,
        PRIMARY KEY (user_id, cin)
    );
""")

conn.commit()
