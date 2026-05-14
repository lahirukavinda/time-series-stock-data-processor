from typing import Dict, List, Tuple, Optional
from app.core.database import get_db_connection

class MarketDataRepository:
    @staticmethod
    def get_annual_data(symbol: str, year: int) -> Optional[Dict[str, str]]:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT MAX(CAST(high AS REAL)) as annual_high,
                   MIN(CAST(low AS REAL))  as annual_low,
                   SUM(CAST(volume AS INTEGER)) as total_volume
            FROM monthly_market_data
            WHERE symbol = ? AND year = ?
        """

        cursor.execute(query, (symbol, year))
        row = cursor.fetchone()

        if row and row["annual_high"] is not None:
            return {
                "high": f"{row['annual_high']:.4f}",
                "low": f"{row['annual_low']:.4f}",
                "volume": str(int(row["total_volume"]))
            }

        return None

    @staticmethod
    def save_monthly_data(symbol: str, monthly_data: List[Tuple]) -> None:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.executemany('''
            INSERT OR IGNORE INTO monthly_market_data
            (symbol, date, year, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', monthly_data)

        conn.commit()

    @staticmethod
    def has_data_for_year(symbol: str, year: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) as count
            FROM monthly_market_data
            WHERE symbol = ? AND year = ?
        """, (symbol, year))

        row = cursor.fetchone()
        return row["count"] > 0
