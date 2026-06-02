from dotenv import load_dotenv
import os
import ccxt

# =========================================================
# LOAD ENV
# =========================================================
load_dotenv()

API_KEY = os.getenv("BITGET_API_KEY")
SECRET = os.getenv("BITGET_SECRET_KEY")
PASSPHRASE = os.getenv("BITGET_PASSPHRASE")

# =========================================================
# BITGET CONNECT
# =========================================================
exchange = ccxt.bitget({
    "apiKey": API_KEY,
    "secret": SECRET,
    "password": PASSPHRASE,
    "enableRateLimit": True
})

# =========================================================
# TEST CONNECTION
# =========================================================
try:
    balance = exchange.fetch_balance({
        "type": "swap"
    })

    print("=" * 50)
    print("BITGET CONNECT SUCCESS")
    print("=" * 50)

    usdt_balance = balance["total"].get("USDT", 0)

    print(f"USDT BALANCE: {usdt_balance}")

except Exception as e:
    print("=" * 50)
    print("BITGET CONNECTION ERROR")
    print("=" * 50)
    print(e)