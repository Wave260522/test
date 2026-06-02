from itertools import combinations

FEATURES = [

    "RSI",
    "RSX",
    "WT",
    "EMA",
    "BOS",
    "SWEEP"

]

def generate_strategies():

    strategies = []

    for r in range(2, len(FEATURES) + 1):

        for combo in combinations(FEATURES, r):

            strategies.append(list(combo))

    return strategies


def show_strategies():

    data = generate_strategies()

    print("=" * 60)
    print("TOTAL STRATEGIES")
    print("=" * 60)

    print(len(data))

    print("=" * 60)

    for i, s in enumerate(data):

        print(i + 1, s)