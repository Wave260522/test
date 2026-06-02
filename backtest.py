from exchange import get_ohlcv
from engine import *

import pandas as pd

# =========================================================
# SINGLE BACKTEST
# =========================================================

def backtest_symbol(
    symbol="BTC/USDT:USDT",
    timeframe="15m",
    limit=1500
):

    ohlcv = get_ohlcv(
        symbol,
        timeframe=timeframe,
        limit=limit
    )

    df = to_dataframe(ohlcv)

    df = apply_indicators(df)

    wins = 0
    losses = 0

    total_pnl = 0

    trades = []

    for i in range(250, len(df) - 10):

        current = df.iloc[:i]

        signal, score = signal_score(current)

        entry = current["close"].iloc[-1]

        future = df.iloc[i:i+10]

        future_close = future["close"].iloc[-1]

        pnl = (
            (future_close - entry)
            / entry
        ) * 100

        # =====================================================
        # LONG
        # =====================================================

        if signal == "LONG":

            if pnl > 0:

                wins += 1

            else:

                losses += 1

            total_pnl += pnl

            trades.append({

                "signal": "LONG",
                "score": score,
                "pnl": pnl

            })

        # =====================================================
        # SHORT
        # =====================================================

        elif signal == "SHORT":

            pnl = -pnl

            if pnl > 0:

                wins += 1

            else:

                losses += 1

            total_pnl += pnl

            trades.append({

                "signal": "SHORT",
                "score": score,
                "pnl": pnl

            })

    # =========================================================
    # RESULT
    # =========================================================

    total = wins + losses

    if total == 0:

        winrate = 0

    else:

        winrate = (
            wins / total
        ) * 100

    avg_pnl = 0

    if total > 0:

        avg_pnl = total_pnl / total

    print("=" * 60)
    print("BACKTEST RESULT")
    print("=" * 60)

    print("SYMBOL:", symbol)
    print("TIMEFRAME:", timeframe)

    print("TRADES:", total)

    print("WINS:", wins)

    print("LOSSES:", losses)

    print(
        "WINRATE:",
        round(winrate, 2),
        "%"
    )

    print(
        "TOTAL PNL:",
        round(total_pnl, 2),
        "%"
    )

    print(
        "AVG PNL:",
        round(avg_pnl, 2),
        "%"
    )

    print("=" * 60)

    return {

        "symbol": symbol,
        "timeframe": timeframe,
        "trades": total,
        "wins": wins,
        "losses": losses,
        "winrate": winrate,
        "total_pnl": total_pnl,
        "avg_pnl": avg_pnl

    }

# =========================================================
# MULTI SYMBOL
# =========================================================

def multi_backtest():

    symbols = [

        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "SOL/USDT:USDT",
        "DOGE/USDT:USDT"

    ]

    timeframes = [

        "5m",
        "15m",
        "1h",
        "4h"

    ]

    results = []

    for symbol in symbols:

        for tf in timeframes:

            result = backtest_symbol(

                symbol=symbol,
                timeframe=tf

            )

            results.append(result)

    # =====================================================
    # DATAFRAME
    # =====================================================

    result_df = pd.DataFrame(results)

    print(result_df)

    # =====================================================
    # SAVE CSV
    # =====================================================

    result_df.to_csv(

        "backtest_results.csv",

        index=False

    )

    print("=" * 60)
    print("CSV SAVED")
    print("=" * 60)