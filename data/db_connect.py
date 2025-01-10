import sqlite3
from importlib import resources


def get_connection():
    with resources.path("data", "tavern_db.db") as db_path:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row  # Enables accessing columns by name
        return conn


def close_connection(conn):
    conn.close()
