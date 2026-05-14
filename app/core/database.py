import sqlite3
import os
import threading

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'market_data.db')

_local = threading.local()

def get_db_connection():
    if not hasattr(_local, 'connection'):
        _local.connection = sqlite3.connect(DB_PATH)
        _local.connection.row_factory = sqlite3.Row
    return _local.connection

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monthly_market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            year INTEGER NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume INTEGER NOT NULL,
            UNIQUE(symbol, date)
        )
    ''')
    conn.commit()

def close_db_connection():
    if hasattr(_local, 'connection'):
        _local.connection.close()
        delattr(_local, 'connection')
