import pandas as pd

pd.set_option('display.max_columns', None)
chess_v1 = "/Users/samuel/PycharmProjects/python-chess/data/move_summary_v1/Hikaru_move_summary.csv"
chess_v2 = "/Users/samuel/PycharmProjects/python-chess/data/cl_v2/Hikaru_combined.csv"
data1, data2 = pd.read_csv(chess_v1), pd.read_csv(chess_v2)

depth1_col = ["depth11", "depth14", "depth20", "depth25"]
depth2_col = ["depth11_v2", "depth14_v2", "depth20_v2", "depth25_v2"]

# Locate most negative observations (top 5 by depth)
bug_counts = {}
bug_cases = {}

for depth in depth2_col:
    best_move_col = depth.replace("_v2", " best move")
    most_neg_moves = data2.nsmallest(5, depth)[["move_number", "move", best_move_col, "fen", depth,]]
    print(f"\nWorst 5 at {depth}:\n{most_neg_moves}")

    mask = (data2["move"] == data2[best_move_col]) & (data2[depth] < 0)
    bugs = data2.loc[mask, ["move_number", "move", best_move_col, depth, "fen"]]

    bug_counts[depth] = len(bugs)
    bug_cases[depth] = bugs

print("\n=== Bug case summary per depth ===")
for depth, count in bug_counts.items():
    print(f"{depth}: {count} cases")

print("\n=== Detailed bug cases ===")
for depth, bugs in bug_cases.items():
    if not bugs.empty:
      print(f"\n⚠️ {depth} ({len(bugs)} cases):")
      print(bugs.head(2))

# Compare version 1 vs version 2 (mean difference per depth)
for d1, d2 in zip(depth1_col, depth2_col):
    diff = (data1[d1].mean() - data2[d2].mean())
    std = (data1[d1].std() - data2[d2].std())
    print(f"Avg difference {d1} vs {d2}: {diff:.2f}")
    print(f"Avg standard deviation {d1} vs {d2}: {std:.2f}")

# calculate the proportion of negative centipawn loss
for depth in depth2_col:
    neg_cl = data2[depth] < 0
    total_observations = len(data2)
    print(f" Depth: {depth}, ({neg_cl.sum()}, {total_observations})")
    print(f" The proportion of negative values to positive values is {neg_cl.sum()/total_observations}")

# Summary stats
for depth in depth2_col:
    print(f"\nSummary {depth}:\n{data2[depth].describe()}")



