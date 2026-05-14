import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'market_data.db')

def seed():
    conn = sqlite3.connect(DB_PATH)
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

    test_data = [
        ('IBM', '2026-05-12', 2026, 234.5500, 235.9500, 219.2200, 219.2200, 43021003),
        ('IBM', '2026-04-30', 2026, 242.1200, 258.5000, 221.7300, 230.9800, 133524534)
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO monthly_market_data 
        (symbol, date, year, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', test_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed()