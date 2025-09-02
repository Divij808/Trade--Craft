# db_setup.py
import sqlite3

def create_db(db_name="tradecraft.db"):
    with sqlite3.connect(db_name) as conn:
        _create_tables(conn)

def create_db_connection(conn):
    _create_tables(conn)

def _create_tables(conn):
    sql_statements = [
        """CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        cash REAL NOT NULL DEFAULT 100000.0);""",

        """CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            qty INTEGER NOT NULL,
            side TEXT NOT NULL,
            price REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );"""
    ]
    cursor = conn.cursor()
    for statement in sql_statements:
        cursor.execute(statement)
    conn.commit()
