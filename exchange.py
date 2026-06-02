from dotenv import load_dotenv
import os
import ccxt
import time

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

API_KEY = os.getenv("BITGET_API_KEY")
SECRET = os.getenv("BITGET_SECRET_KEY")
PASSPHRASE = os.getenv("BITGET_PASSPHRASE")

# =========================================================
# CONNECT
# =========================================================

exchange = ccxt.bitget({

    "apiKey": API_KEY,
    "secret": SECRET,
    "password": PASSPHRASE,

    "enableRateLimit": True,

    "options": {
        "defaultType": "swap"
    }

})

# =========================================================
# MARKET LOAD
# =========================================================

exchange.load_markets()

# =========================================================
# GET BALANCE
# =========================================================

def get_balance():

    try:

        balance = exchange.fetch_balance()

        usdt = balance["total"].get("USDT", 0)

        return float(usdt)

    except Exception as e:

        print("BALANCE ERROR", e)

        return 0.0

# =========================================================
# GET PRICE
# =========================================================

def get_price(symbol):

    try:

        ticker = exchange.fetch_ticker(symbol)

        return float(ticker["last"])

    except Exception as e:

        print("PRICE ERROR", e)

        return None

# =========================================================
# SET LEVERAGE
# =========================================================

def set_leverage(symbol, leverage):

    try:

        exchange.set_leverage(

            leverage,

            symbol

        )

        return True

    except Exception as e:

        print("LEVERAGE ERROR", e)

        return False

# =========================================================
# MARKET ORDER
# =========================================================

def market_order(

    symbol,
    side,
    usd_size,
    leverage=5

):

    try:

        price = get_price(symbol)

        if price is None:
            return None

        set_leverage(symbol, leverage)

        amount = (

            usd_size * leverage

        ) / price

        amount = round(amount, 3)

        order_side = (

            "buy"
            if side == "LONG"
            else "sell"

        )

        order = exchange.create_market_order(

            symbol=symbol,

            side=order_side,

            amount=amount

        )

        print("=" * 50)
        print("ORDER SUCCESS")
        print("=" * 50)

        print(symbol)
        print(side)
        print(amount)

        return order

    except Exception as e:

        print("=" * 50)
        print("ORDER ERROR")
        print("=" * 50)

        print(e)

        return None

# =========================================================
# CLOSE POSITION
# =========================================================

def close_position(

    symbol,
    side,
    amount

):

    try:

        close_side = (

            "sell"
            if side == "LONG"
            else "buy"

        )

        order = exchange.create_market_order(

            symbol=symbol,

            side=close_side,

            amount=amount,

            params={
                "reduceOnly": True
            }

        )

        return order

    except Exception as e:

        print("CLOSE ERROR", e)

        return None

# =========================================================
# OHLCV
# =========================================================

def get_ohlcv(

    symbol,
    timeframe="5m",
    limit=300

):

    try:

        ohlcv = exchange.fetch_ohlcv(

            symbol,

            timeframe=timeframe,

            limit=limit

        )

        return ohlcv

    except Exception as e:

        print("OHLCV ERROR", e)

        return None

# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 50)

    print("BITGET TEST")

    print("=" * 50)

    balance = get_balance()

    print("USDT:", balance)

    price = get_price("BTC/USDT:USDT")

    print("BTC:", price)