# utils/api_handler.py
import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

class BitgetHandler:
    def __init__(self):
        self.exchange = ccxt.bitget({
            'apiKey': os.getenv("BITGET_API_KEY"),
            'secret': os.getenv("BITGET_SECRET_KEY"),
            'password': os.getenv("BITGET_PASSPHRASE"),
            'enableRateLimit': True,
        })

    def fetch_balance(self):
        try:
            return self.exchange.fetch_balance()
        except Exception as e:
            return f"Error: {e}"