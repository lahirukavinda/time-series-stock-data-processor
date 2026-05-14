import pytest
import sqlite3
import os
from app.core.repository import MarketDataRepository
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
def sample_data():
    return [
        ("IBM", "2026-05-01", 2026, 100.0, 110.0, 95.0, 105.0, 1000000),
        ("IBM", "2026-04-01", 2026, 105.0, 115.0, 100.0, 110.0, 1200000),
        ("AAPL", "2026-05-01", 2026, 200.0, 210.0, 195.0, 205.0, 2000000),
    ]


def test_save_and_get_annual_data(sample_data):
    MarketDataRepository.save_monthly_data("IBM", sample_data[:2])  # IBM data only

    result = MarketDataRepository.get_annual_data("IBM", 2026)
    assert result is not None
    assert result["high"] == "115.0000"
    assert result["low"] == "95.0000"
    assert result["volume"] == "2200000"

    result = MarketDataRepository.get_annual_data("IBM", 2025)
    assert result is None

    result = MarketDataRepository.get_annual_data("NONEXISTENT", 2026)
    assert result is None


def test_has_data_for_year(sample_data):
    MarketDataRepository.save_monthly_data("AAPL", [sample_data[2]])  # AAPL data

    assert MarketDataRepository.has_data_for_year("AAPL", 2026) == True

    assert MarketDataRepository.has_data_for_year("AAPL", 2025) == False
    assert MarketDataRepository.has_data_for_year("GOOGL", 2026) == False
