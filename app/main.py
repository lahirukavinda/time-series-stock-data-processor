from fastapi import FastAPI, HTTPException
from typing import Dict

from app.core.database import init_db, get_db_connection

def get_application() -> FastAPI:
    _app = FastAPI()
    init_db()
    return _app
app = get_application()

@app.get("/symbols/{symbol}/annual/{year}")
async def market_data_fetch(
    symbol: str,
    year: int
) -> Dict:
    symbol = symbol.upper()
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
            SELECT MAX(high)   as annual_high, \
                   MIN(low)    as annual_low, \
                   SUM(volume) as total_volume
            FROM monthly_market_data
            WHERE symbol = ? AND year = ? \
            """

    cursor.execute(query, (symbol, year))
    row = cursor.fetchone()
    conn.close()

    if row and row["annual_high"] is not None:
        return {
            "high": f"{row['annual_high']:.4f}",
            "low": f"{row['annual_low']:.4f}",
            "volume": str(row["total_volume"])
        }

    raise HTTPException(status_code=404, detail="Market data not found for symbol: {}, year: {}".format(symbol, year))