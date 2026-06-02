import numpy as np
import pandas as pd

# =========================================================
# DATAFRAME
# =========================================================

def to_dataframe(ohlcv):

    df = pd.DataFrame(

        ohlcv,

        columns=[
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]

    )

    return df

# =========================================================
# EMA
# =========================================================

def ema(series, period):

    return series.ewm(
        span=period,
        adjust=False
    ).mean()

# =========================================================
# RSI
# =========================================================

def rsi(df, period=14):

    delta = df["close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    value = (
        100 -
        (100 / (1 + rs))
    )

    df["rsi"] = value

    return df

# =========================================================
# RSX
# =========================================================

def rsx(df, period=14):

    price = df["close"]

    alpha = 3 / (period + 2)

    rsx = price.copy()

    for i in range(1, len(price)):

        rsx.iloc[i] = (

            alpha * price.iloc[i]

            +

            (1 - alpha)

            *

            rsx.iloc[i - 1]

        )

    min_val = rsx.rolling(period).min()

    max_val = rsx.rolling(period).max()

    rsx_norm = (
        (rsx - min_val)
        /
        (max_val - min_val)
    ) * 100

    df["rsx"] = rsx_norm

    return df

# =========================================================
# WAVETREND
# =========================================================

def wavetrend(df):

    ap = (
        df["high"] +
        df["low"] +
        df["close"]
    ) / 3

    esa = ap.ewm(span=10).mean()

    d = abs(ap - esa).ewm(span=10).mean()

    ci = (
        ap - esa
    ) / (0.015 * d)

    wt1 = ci.ewm(span=21).mean()

    wt2 = wt1.rolling(4).mean()

    df["wt1"] = wt1
    df["wt2"] = wt2

    return df

# =========================================================
# ATR
# =========================================================

def atr(df, period=14):

    hl = df["high"] - df["low"]

    hc = abs(
        df["high"] -
        df["close"].shift()
    )

    lc = abs(
        df["low"] -
        df["close"].shift()
    )

    tr = pd.concat(
        [hl, hc, lc],
        axis=1
    ).max(axis=1)

    atr = tr.rolling(period).mean()

    df["atr"] = atr

    return df

# =========================================================
# VOLUME POWER
# =========================================================

def volume_power(df):

    vol_ma = (
        df["volume"]
        .rolling(20)
        .mean()
    )

    ratio = (
        df["volume"] /
        vol_ma
    )

    df["vol_ratio"] = ratio

    return df

# =========================================================
# TREND
# =========================================================

def trend(df):

    df["ema20"] = ema(
        df["close"],
        20
    )

    df["ema50"] = ema(
        df["close"],
        50
    )

    df["ema200"] = ema(
        df["close"],
        200
    )

    return df

# =========================================================
# PIVOT HIGH
# =========================================================

def detect_pivot_high(df, left=3, right=3):

    highs = df["high"]

    pivot = []

    for i in range(len(df)):

        if i < left or i + right >= len(df):

            pivot.append(False)

            continue

        val = highs.iloc[i]

        is_pivot = True

        for j in range(i - left, i + right + 1):

            if highs.iloc[j] > val:

                is_pivot = False
                break

        pivot.append(is_pivot)

    df["pivot_high"] = pivot

    return df

# =========================================================
# PIVOT LOW
# =========================================================

def detect_pivot_low(df, left=3, right=3):

    lows = df["low"]

    pivot = []

    for i in range(len(df)):

        if i < left or i + right >= len(df):

            pivot.append(False)

            continue

        val = lows.iloc[i]

        is_pivot = True

        for j in range(i - left, i + right + 1):

            if lows.iloc[j] < val:

                is_pivot = False
                break

        pivot.append(is_pivot)

    df["pivot_low"] = pivot

    return df

# =========================================================
# BOS
# =========================================================

def detect_bos(df):

    bos = []

    last_high = None

    for i in range(len(df)):

        if df["pivot_high"].iloc[i]:

            last_high = df["high"].iloc[i]

        if last_high is not None:

            if df["close"].iloc[i] > last_high:

                bos.append(True)

            else:

                bos.append(False)

        else:

            bos.append(False)

    df["bos"] = bos

    return df

# =========================================================
# LIQUIDITY SWEEP
# =========================================================

def liquidity_sweep(df):

    sweep = []

    for i in range(1, len(df)):

        prev_high = df["high"].iloc[i - 1]

        current_high = df["high"].iloc[i]

        current_close = df["close"].iloc[i]

        if current_high > prev_high and current_close < prev_high:

            sweep.append(True)

        else:

            sweep.append(False)

    sweep.insert(0, False)

    df["sweep"] = sweep

    return df

# =========================================================
# APPLY INDICATORS
# =========================================================

def apply_indicators(df):

    df = trend(df)

    df = rsi(df)

    df = rsx(df)

    df = wavetrend(df)

    df = atr(df)

    df = volume_power(df)

    df = detect_pivot_high(df)

    df = detect_pivot_low(df)

    df = detect_bos(df)

    df = liquidity_sweep(df)

    return df

# =========================================================
# SIGNAL ENGINE
# =========================================================

def signal_score(df, strategy=None):

    if strategy is None:

        strategy = [

            "RSI",
            "RSX",
            "WT",
            "EMA",
            "BOS",
            "SWEEP"

        ]

    long_score = 0
    short_score = 0

    rsi_now = df["rsi"].iloc[-1]

    rsx_now = df["rsx"].iloc[-1]

    wt1 = df["wt1"].iloc[-1]
    wt2 = df["wt2"].iloc[-1]

    price = df["close"].iloc[-1]

    ema20 = df["ema20"].iloc[-1]
    ema50 = df["ema50"].iloc[-1]
    ema200 = df["ema200"].iloc[-1]

    vol = df["vol_ratio"].iloc[-1]

    bos = df["bos"].iloc[-1]

    sweep = df["sweep"].iloc[-1]

    # =====================================================
    # TREND
    # =====================================================

   if "EMA" in strategy:

    if price > ema20 > ema50 > ema200:

        long_score += 30

    if price < ema20 < ema50 < ema200:

        short_score += 30

    # =====================================================
    # RSI
    # =====================================================

    if "RSI" in strategy:

    if rsi_now < 35:

        long_score += 15

    if rsi_now > 65:

        short_score += 15

    # =====================================================
    # RSX
    # =====================================================

    if "RSX" in strategy:

    if rsx_now < 30:

        long_score += 15

    if rsx_now > 70:

        short_score += 15

    # =====================================================
    # WT
    # =====================================================

    if "WT" in strategy:

    if wt1 > wt2:

        long_score += 20

    if wt1 < wt2:

        short_score += 20

    # =====================================================
    # VOLUME
    # =====================================================

    if vol > 1.5:

        long_score += 10
        short_score += 10

    # =====================================================
    # BOS
    # =====================================================

    if "BOS" in strategy:

    if bos:

        long_score += 20

    # =====================================================
    # SWEEP
    # =====================================================

    if "SWEEP" in strategy:

    if sweep:

        short_score += 25

    # =====================================================
    # RESULT
    # =====================================================

    if long_score >= 70:
        return "LONG", long_score

    if short_score >= 70:
        return "SHORT", short_score

    return None, 0

# =========================================================
# DEBUG
# =========================================================

def debug_signal(df):

    long_score = 0
    short_score = 0

    print("=" * 50)
    print("DEBUG SIGNAL")
    print("=" * 50)

    print("PRICE:", df["close"].iloc[-1])

    print("EMA20:", round(df["ema20"].iloc[-1], 2))
    print("EMA50:", round(df["ema50"].iloc[-1], 2))
    print("EMA200:", round(df["ema200"].iloc[-1], 2))

    print("RSI:", round(df["rsi"].iloc[-1], 2))

    print("RSX:", round(df["rsx"].iloc[-1], 2))

    print("WT1:", round(df["wt1"].iloc[-1], 2))
    print("WT2:", round(df["wt2"].iloc[-1], 2))

    print("VOL RATIO:", round(df["vol_ratio"].iloc[-1], 2))

    print("BOS:", df["bos"].iloc[-1])

    print("SWEEP:", df["sweep"].iloc[-1])

    if df["wt1"].iloc[-1] > df["wt2"].iloc[-1]:

        long_score += 20

        print("WT LONG +20")

    if df["wt1"].iloc[-1] < df["wt2"].iloc[-1]:

        short_score += 20

        print("WT SHORT +20")

    print("=" * 50)

    print("LONG SCORE:", long_score)

    print("SHORT SCORE:", short_score)

    print("=" * 50)

    if long_score > short_score:

        print("FINAL: LONG")

    elif short_score > long_score:

        print("FINAL: SHORT")

    else:

        print("FINAL: NEUTRAL")

    print("=" * 50)