import numpy as np

# =========================================================
# BULLISH DIVERGENCE
# =========================================================

def bullish_divergence(df):

    try:

        if len(df) < 50:
            return False

        price1 = df["low"].iloc[-30:-15].min()
        price2 = df["low"].iloc[-15:].min()

        wt1 = df["wt1"].iloc[-30:-15].min()
        wt2 = df["wt1"].iloc[-15:].min()

        if (

            price2 < price1

            and

            wt2 > wt1

        ):

            return True

        return False

    except:

        return False


# =========================================================
# BEARISH DIVERGENCE
# =========================================================

def bearish_divergence(df):

    try:

        if len(df) < 50:
            return False

        price1 = df["high"].iloc[-30:-15].max()
        price2 = df["high"].iloc[-15:].max()

        wt1 = df["wt1"].iloc[-30:-15].max()
        wt2 = df["wt1"].iloc[-15:].max()

        if (

            price2 > price1

            and

            wt2 < wt1

        ):

            return True

        return False

    except:

        return False


# =========================================================
# MAIN
# =========================================================

def divergence_signal(df):

    if bullish_divergence(df):
        return "LONG"

    if bearish_divergence(df):
        return "SHORT"

    return None