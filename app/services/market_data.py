import httpx
from fastapi import HTTPException
from typing import Dict
from app.core.repository import MarketDataRepository
from app.core.settings import ALPHA_VANTAGE_URL, API_KEY, HTTP_TIMEOUT


async def fetch_and_save_data(symbol: str, year: int) -> Dict[str, str] | None:
    params = {
        "function": "TIME_SERIES_MONTHLY",
        "symbol": symbol,
        "apikey": API_KEY
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(ALPHA_VANTAGE_URL, params=params, timeout=HTTP_TIMEOUT)
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="External API error")

            data = response.json()

            if "Error Message" in data:
                raise HTTPException(status_code=404, detail="Symbol not found on Alpha Vantage")

            monthly_series = data.get("Monthly Time Series", {})

            if not monthly_series:
                return None

            # Prepare data for bulk insert
            monthly_data = []
            data_found_for_year = False

            for date_str, metrics in monthly_series.items():
                year_int = int(date_str.split("-")[0])

                monthly_data.append((
                    symbol, date_str, year_int,
                    float(metrics["1. open"]),
                    float(metrics["2. high"]),
                    float(metrics["3. low"]),
                    float(metrics["4. close"]),
                    int(metrics["5. volume"])
                ))

                if year_int == year:
                    data_found_for_year = True

            if not data_found_for_year:
                return None

            MarketDataRepository.save_monthly_data(symbol, monthly_data)

            return MarketDataRepository.get_annual_data(symbol, year)

    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Failed to reach Alpha Vantage API: {str(e)}")
