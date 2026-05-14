import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'market_data.db')

ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")

HTTP_TIMEOUT = 30.0