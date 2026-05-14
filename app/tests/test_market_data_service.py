import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from app.services.market_data import fetch_and_save_data


@pytest.mark.asyncio
async def test_fetch_and_save_data_success():
    """Test successful API call and data saving"""
    mock_response_data = {
        "Monthly Time Series": {
            "2026-05-01": {
                "1. open": "100.0000",
                "2. high": "110.0000",
                "3. low": "95.0000",
                "4. close": "105.0000",
                "5. volume": "1000000"
            },
            "2026-04-01": {
                "1. open": "105.0000",
                "2. high": "115.0000",
                "3. low": "100.0000",
                "4. close": "110.0000",
                "5. volume": "1200000"
            }
        }
    }

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: mock_response_data  # Make json a callable that returns data
        mock_get.return_value = mock_response

        result = await fetch_and_save_data("IBM", 2026)

        assert result is not None
        assert result["high"] == "115.0000"
        assert result["low"] == "95.0000"
        assert result["volume"] == "2200000"


@pytest.mark.asyncio
async def test_fetch_and_save_data_symbol_not_found():
    """Test API call when symbol doesn't exist"""
    mock_response_data = {
        "Error Message": "Invalid API call. Please retry or visit the documentation"
    }

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: mock_response_data  # Make json a callable that returns data
        mock_get.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            await fetch_and_save_data("INVALID", 2026)

        assert exc_info.value.status_code == 404
        assert "Symbol not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_fetch_and_save_data_no_data_for_year():
    """Test API call when symbol exists but no data for requested year"""
    mock_response_data = {
        "Monthly Time Series": {
            "2025-05-01": {  # Data for 2025, not 2026
                "1. open": "100.0000",
                "2. high": "110.0000",
                "3. low": "95.0000",
                "4. close": "105.0000",
                "5. volume": "1000000"
            }
        }
    }

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: mock_response_data  # Make json a callable that returns data
        mock_get.return_value = mock_response

        result = await fetch_and_save_data("IBM", 2026)
        assert result is None


@pytest.mark.asyncio
async def test_fetch_and_save_data_api_error():
    """Test API call failure"""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            await fetch_and_save_data("IBM", 2026)

        assert exc_info.value.status_code == 502
        assert "External API error" in exc_info.value.detail
