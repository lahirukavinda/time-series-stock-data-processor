import pytest
import sqlite3
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.core.database import init_db, close_db_connection


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    init_db()
    yield
    close_db_connection()


@pytest.fixture(scope="function", autouse=True)
def clean_database():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'market_data.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM monthly_market_data")
    conn.commit()
    conn.close()

    yield

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM monthly_market_data")
    conn.commit()
    conn.close()


@pytest.fixture
def client():
    return TestClient(app)


def test_get_market_data_cached(client):
    from app.core.repository import MarketDataRepository
    test_data = [
        ("IBM", "2026-05-01", 2026, 100.0, 110.0, 95.0, 105.0, 1000000),
        ("IBM", "2026-04-01", 2026, 105.0, 115.0, 100.0, 110.0, 1200000),
    ]
    MarketDataRepository.save_monthly_data("IBM", test_data)

    response = client.get("/symbols/IBM/annual/2026")

    assert response.status_code == 200
    data = response.json()
    assert data["high"] == "115.0000"
    assert data["low"] == "95.0000"
    assert data["volume"] == "2200000"


def test_get_market_data_not_found(client):
    """Test requesting data that doesn't exist"""
    mock_response_data = {
        "Error Message": "Invalid API call. Please retry or visit the documentation"
    }

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: mock_response_data  # Make json a callable that returns data
        mock_get.return_value = mock_response

        response = client.get("/symbols/NONEXISTENT/annual/2025")

        assert response.status_code == 404
        assert "Symbol not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_market_data_fetch_from_api(client):
    """Test fetching data from external API when not cached"""
    mock_response_data = {
        "Monthly Time Series": {
            "2025-05-01": {
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

        response = client.get("/symbols/IBM/annual/2025")

        assert response.status_code == 200
        data = response.json()
        assert data["high"] == "110.0000"
        assert data["low"] == "95.0000"
        assert data["volume"] == "1000000"


@pytest.mark.asyncio
async def test_get_market_data_api_symbol_not_found(client):
    """Test API returns symbol not found"""
    mock_response_data = {
        "Error Message": "Invalid API call. Please retry or visit the documentation"
    }

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = lambda: mock_response_data  # Make json a callable that returns data
        mock_get.return_value = mock_response

        response = client.get("/symbols/INVALID/annual/2025")

        assert response.status_code == 404
        assert "Symbol not found" in response.json()["detail"]


def test_symbol_case_insensitive(client):
    """Test that symbol is handled case-insensitively"""
    # Seed data with uppercase symbol
    from app.core.repository import MarketDataRepository
    test_data = [
        ("AAPL", "2026-05-01", 2026, 200.0, 210.0, 195.0, 205.0, 1000000),
    ]
    MarketDataRepository.save_monthly_data("AAPL", test_data)

    # Request with lowercase
    response = client.get("/symbols/aapl/annual/2026")

    assert response.status_code == 200
    data = response.json()
    assert data["high"] == "210.0000"
