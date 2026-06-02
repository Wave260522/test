from exchange import get_ohlcv
from engine import *

import itertools
import pandas as pd
import warnings

warnings.filterwarnings("ignore")
# =========================================================
# SETTINGS
# =========================================================

LOOKBACK = 10000

SL = 1.0
TP1 = 1.5
TP2 = 3.0

BE_TRIGGER = 1.0
TRAILING = 0.8

MAX_HOLD_BARS = 50

# =========================================================
# STRATEGIES
# =========================================================

INDICATORS = [

    "RSI",
    "RSX",
    "WT",
    "EMA",
    "BOS",
    "SWEEP"

]

# =========================================================
# GENERATE STRATEGIES
# =========================================================

def generate_strategies():

    strategies = []

    for r in range(2, len(INDICATORS) + 1):

        combos = itertools.combinations(
            INDICATORS,
            r
        )

        for combo in combos:

            strategies.append(
                list(combo)
            )

    return strategies

# =========================================================
# TRADE SIMULATOR
# =========================================================

def simulate_trade(

    df,
    start_idx,
    signal,
    entry

):

    if signal == "LONG":

        sl_price = entry * (1 - SL / 100)

        tp1_price = entry * (1 + TP1 / 100)

        tp2_price = entry * (1 + TP2 / 100)

    else:

        sl_price = entry * (1 + SL / 100)

        tp1_price = entry * (1 - TP1 / 100)

        tp2_price = entry * (1 - TP2 / 100)

    be_active = False

    highest = entry
    lowest = entry

    tp1_hit = False

    end_bar = min(

        start_idx + MAX_HOLD_BARS,

        len(df) - 1

    )

    for j in range(

        start_idx + 1,

        end_bar + 1

    ):

        high = df["high"].iloc[j]

        low = df["low"].iloc[j]

        close = df["close"].iloc[j]

        # =====================================================
        # LONG
        # =====================================================

        if signal == "LONG":

            highest = max(
                highest,
                high
            )

            if (

                not tp1_hit

                and

                high >= tp1_price

            ):

                tp1_hit = True

            if (

                not be_active

                and

                high >= entry * (

                    1 + BE_TRIGGER / 100

                )

            ):

                sl_price = entry

                be_active = True

            trail_price = (

                highest

                *

                (

                    1 - TRAILING / 100

                )

            )

            if high >= tp2_price:

                return TP2

            if (

                be_active

                and

                low <= trail_price

            ):

                return (

                    (trail_price - entry)

                    /

                    entry

                ) * 100

            if low <= sl_price:

                return (

                    (sl_price - entry)

                    /

                    entry

                ) * 100

        # =====================================================
        # SHORT
        # =====================================================

        else:

            lowest = min(
                lowest,
                low
            )

            if (

                not tp1_hit

                and

                low <= tp1_price

            ):

                tp1_hit = True

            if (

                not be_active

                and

                low <= entry * (

                    1 - BE_TRIGGER / 100

                )

            ):

                sl_price = entry

                be_active = True

            trail_price = (

                lowest

                *

                (

                    1 + TRAILING / 100

                )

            )

            if low <= tp2_price:

                return TP2

            if (

                be_active

                and

                high >= trail_price

            ):

                return (

                    (entry - trail_price)

                    /

                    entry

                ) * 100

            if high >= sl_price:

                return (

                    (entry - sl_price)

                    /

                    entry

                ) * 100

    # =====================================================
    # TIME EXIT
    # =====================================================

    final_close = df["close"].iloc[end_bar]

    if signal == "LONG":

        return (

            (final_close - entry)

            /

            entry

        ) * 100

    else:

        return (

            (entry - final_close)

            /

            entry

        ) * 100
    # =========================================================
# TEST STRATEGY
# =========================================================

def test_strategy(

    symbol,
    timeframe,
    strategy

):

    try:

        ohlcv = get_ohlcv(

            symbol,

            timeframe=timeframe,

            limit=LOOKBACK

        )

        if ohlcv is None:

            return None

        if len(ohlcv) < 300:

            return None

        df = to_dataframe(ohlcv)

        df = apply_indicators(df)

    except Exception as e:

        print(

            "DATA ERROR:",

            symbol,

            timeframe,

            e

        )

        return None

    wins = 0
    losses = 0

    total_pnl = 0

    trades = []

    # =====================================================
    # MAIN LOOP
    # =====================================================

    for i in range(

        250,

        len(df) - MAX_HOLD_BARS - 1

    ):

        current = df.iloc[:i]

        try:

            signal, score = signal_score(

                current,

                strategy

            )

        except Exception:

            continue

        if signal is None:

            continue

        entry = current["close"].iloc[-1]

        pnl = simulate_trade(

            df=df,

            start_idx=i,

            signal=signal,

            entry=entry

        )

        total_pnl += pnl

        if pnl > 0:

            wins += 1

        else:

            losses += 1

        trades.append(

            {

                "signal": signal,

                "score": score,

                "pnl": pnl

            }

        )

    # =====================================================
    # RESULT
    # =====================================================

    total_trades = wins + losses

    if total_trades == 0:

        return None

    winrate = (

        wins

        /

        total_trades

    ) * 100

    avg_pnl = (

        total_pnl

        /

        total_trades

    )

    max_win = 0
    max_loss = 0

    if len(trades) > 0:

        pnl_list = [

            x["pnl"]

            for x in trades

        ]

        max_win = max(pnl_list)

        max_loss = min(pnl_list)

    return {

        "symbol": symbol,

        "timeframe": timeframe,

        "strategy": ",".join(strategy),

        "trades": total_trades,

        "wins": wins,

        "losses": losses,

        "winrate": round(

            winrate,

            2

        ),

        "total_pnl": round(

            total_pnl,

            2

        ),

        "avg_pnl": round(

            avg_pnl,

            4

        ),

        "best_trade": round(

            max_win,

            2

        ),

        "worst_trade": round(

            max_loss,

            2

        )

    }
# =========================================================
# OPTIMIZER
# =========================================================

def optimize():

    strategies = generate_strategies()

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

    total_tests = (

        len(symbols)

        *

        len(timeframes)

        *

        len(strategies)

    )

    count = 0

    print("=" * 60)
    print("START OPTIMIZER V2")
    print("TOTAL TEST:", total_tests)
    print("=" * 60)

    for symbol in symbols:

        for timeframe in timeframes:

            for strategy in strategies:

                count += 1

                print(

                    f"[{count}/{total_tests}]",

                    symbol,

                    timeframe,

                    strategy

                )

                result = test_strategy(

                    symbol,

                    timeframe,

                    strategy

                )

                if result is not None:

                    results.append(

                        result

                    )

    if len(results) == 0:

        print("NO RESULTS")

        return None

    df = pd.DataFrame(results)

    # =====================================================
    # SORT
    # =====================================================

    df = df.sort_values(

        by=[

            "total_pnl",
            "winrate"

        ],

        ascending=False

    )

    # =====================================================
    # SAVE
    # =====================================================

    filename = (

        "optimizer_results_v2.csv"

    )

    df.to_csv(

        filename,

        index=False

    )

    # =====================================================
    # TOP 20
    # =====================================================

    print()

    print("=" * 60)
    print("TOP 20 STRATEGIES")
    print("=" * 60)

    print(

        df.head(20)

    )

    print("=" * 60)
    print("ROWS:", len(df))
    print("FILE:", filename)
    print("=" * 60)

    return df


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    optimize()
    