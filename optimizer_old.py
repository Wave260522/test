from exchange import get_ohlcv
from engine_old import *

import itertools
import pandas as pd

# =========================================================
# PARAM GRID
# =========================================================

RSI_LONG_RANGE = [25, 30, 35, 40]

RSI_SHORT_RANGE = [60, 65, 70, 75]

WT_SCORE_RANGE = [10, 20, 30]

VOLUME_RANGE = [1.2, 1.5, 2.0]

# =========================================================
# TEST ENGINE
# =========================================================

def run_strategy(

    symbol,
    rsi_long,
    rsi_short,
    wt_score,
    vol_ratio

):

    ohlcv = get_ohlcv(symbol)

    df = to_dataframe(ohlcv)

    df = apply_indicators(df)

    pnl = 0

    trades = 0

    wins = 0

    losses = 0

    for i in range(250, len(df)-5):

        row = df.iloc[i]

        long_score = 0
        short_score = 0

        # =====================================================
        # TREND
        # =====================================================

        if row["close"] > row["ema20"] > row["ema50"]:

            long_score += 30

        if row["close"] < row["ema20"] < row["ema50"]:

            short_score += 30

        # =====================================================
        # RSI
        # =====================================================

        if row["rsi"] < rsi_long:

            long_score += 20

        if row["rsi"] > rsi_short:

            short_score += 20

        # =====================================================
        # WT
        # =====================================================

        if row["wt1"] > row["wt2"]:

            long_score += wt_score

        if row["wt1"] < row["wt2"]:

            short_score += wt_score

        # =====================================================
        # VOLUME
        # =====================================================

        if row["vol_ratio"] > vol_ratio:

            long_score += 10
            short_score += 10

        # =====================================================
        # LONG
        # =====================================================

        if long_score >= 70:

            entry = row["close"]

            exit_price = df.iloc[i+5]["close"]

            result = (

                (exit_price - entry)
                /
                entry

            ) * 100

            pnl += result

            trades += 1

            if result > 0:
                wins += 1
            else:
                losses += 1

        # =====================================================
        # SHORT
        # =====================================================

        if short_score >= 70:

            entry = row["close"]

            exit_price = df.iloc[i+5]["close"]

            result = (

                (entry - exit_price)
                /
                entry

            ) * 100

            pnl += result

            trades += 1

            if result > 0:
                wins += 1
            else:
                losses += 1

    if trades == 0:

        return None

    winrate = (wins / trades) * 100

    return {

        "symbol": symbol,
        "rsi_long": rsi_long,
        "rsi_short": rsi_short,
        "wt_score": wt_score,
        "vol_ratio": vol_ratio,
        "trades": trades,
        "winrate": round(winrate, 2),
        "pnl": round(pnl, 2)

    }

# =========================================================
# OPTIMIZER
# =========================================================

def optimize(symbol="BTC/USDT:USDT"):

    results = []

    combos = itertools.product(

        RSI_LONG_RANGE,
        RSI_SHORT_RANGE,
        WT_SCORE_RANGE,
        VOLUME_RANGE

    )

    for combo in combos:

        result = run_strategy(

            symbol,
            combo[0],
            combo[1],
            combo[2],
            combo[3]

        )

        if result:

            results.append(result)

            print(result)

    df = pd.DataFrame(results)

    df = df.sort_values(

        by="pnl",
        ascending=False

    )

    print("=" * 70)
    print("TOP RESULTS")
    print("=" * 70)

    print(df.head(10))

    return df