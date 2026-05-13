from fastapi import FastAPI, HTTPException
from typing import Dict

def get_application() -> FastAPI:
    return FastAPI()
app = get_application()

@app.get("/symbols/{symbol}/annual/{year}")
async def market_data_fetch(
    symbol: str,
    year: int
) -> Dict :
    if symbol == "IBM" and year == 2005:
        return {
            "high": "80.8700",
            "low": "76.0600",
            "volume": "139457800"
        }

    raise HTTPException(status_code=404, detail="Market data not found for symbol: {}, year: {}".format(symbol, year))