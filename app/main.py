from fastapi import FastAPI, HTTPException
from typing import Dict

from app.core.database import init_db
from app.core.repository import MarketDataRepository
from app.services.market_data import fetch_and_save_data

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
    cached_data = MarketDataRepository.get_annual_data(symbol, year)

    if cached_data:
        return cached_data

    try:
        aggregated_data = await fetch_and_save_data(symbol, year)

        if not aggregated_data:
            raise HTTPException(
                status_code=404,
                detail=f"No market data available for symbol {symbol} in year {year}"
            )

        return aggregated_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing market data: {str(e)}"
        )
