# Time Series Stock Data Processor

REST API to fetch stock market data from Alpha Vantage, cache it in SQLite, and return annual aggregations.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your Alpha Vantage API key
```

Get API key: https://www.alphavantage.co/support/#api-key

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

## Test

```bash
# Run all tests
pytest

# Run specific test file
pytest app/tests/test_repository.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run tests in verbose mode
pytest -v
```

## API

### GET /symbols/{symbol}/annual/{year}

Returns annual market data (high, low, volume) for a symbol in a given year.

**Example:**
```bash
curl "http://localhost:8000/symbols/IBM/annual/2005"
```

**Response:**
```json
{
  "high": "80.8700",
  "low": "76.0600",
  "volume": "139457800"
}
```

## How It Works

1. Check local database for data
2. If not found, fetch from Alpha Vantage API
3. Store in database
4. Return aggregated values

## Database

SQLite with monthly market data. Schema:

```sql
CREATE TABLE monthly_market_data (
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
```

## Project Structure

```
app/
├── main.py              # FastAPI endpoint
├── core/
│   ├── database.py      # Database connection
│   └── repository.py    # Data access layer
├── services/
│   └── market_data.py   # Alpha Vantage integration
└── tests/
    ├── test_repository.py     # Repository tests
    ├── test_market_data_service.py  # Service tests
    └── test_api.py           # API endpoint tests
```
