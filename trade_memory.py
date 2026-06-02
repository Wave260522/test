import json
import os
from datetime import datetime

MEMORY_FILE = "trade_memory.json"

# =========================================================
# LOAD MEMORY
# =========================================================

def load_memory():

    if not os.path.exists(MEMORY_FILE):

        return []

    with open(MEMORY_FILE, "r") as f:

        return json.load(f)

# =========================================================
# SAVE MEMORY
# =========================================================

def save_memory(data):

    with open(MEMORY_FILE, "w") as f:

        json.dump(
            data,
            f,
            indent=4
        )

# =========================================================
# ADD TRADE
# =========================================================

def add_trade(

    symbol,
    side,
    entry,
    exit_price,
    pnl,
    state,
    strategy,
    score

):

    memory = load_memory()

    trade = {

        "time": str(datetime.now()),

        "symbol": symbol,

        "side": side,

        "entry": entry,

        "exit": exit_price,

        "pnl": pnl,

        "market_state": state,

        "strategy": strategy,

        "score": score

    }

    memory.append(trade)

    save_memory(memory)

# =========================================================
# STATS
# =========================================================

def stats():

    memory = load_memory()

    if len(memory) == 0:

        print("NO MEMORY")
        return

    wins = 0
    losses = 0

    total = 0

    for t in memory:

        pnl = t["pnl"]

        total += pnl

        if pnl > 0:

            wins += 1

        else:

            losses += 1

    total_trades = wins + losses

    winrate = (

        wins / total_trades

    ) * 100

    avg = total / total_trades

    print("=" * 50)

    print("AI MEMORY REPORT")

    print("=" * 50)

    print("TRADES:", total_trades)

    print("WINS:", wins)

    print("LOSSES:", losses)

    print("WINRATE:", round(winrate, 2), "%")

    print("TOTAL PNL:", round(total, 2), "%")

    print("AVG:", round(avg, 2), "%")

    print("=" * 50)