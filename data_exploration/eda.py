import pandas as pd
from arrange_data import order_chess_columns
import ast
import re

pd.set_option('display.max_columns', None)

# Step 1 : Combined game_info and ()* for new cl_v2
files = {
    "HikaruI": "/Users/samuel/PycharmProjects/python-chess/data/cl_v2/TSMFTXH_eval_v2.csv",
    "HikaruG": "/Users/samuel/PycharmProjects/python-chess/data/cl_v2/TSMFTXH_game_info.csv",
    "HikaruC": "/Users/samuel/PycharmProjects/python-chess/data/cl_v2/TSMFTXH_move_v2(with checkmate detection).csv",
    "HikaruL": "/Users/samuel/PycharmProjects/python-chess/data/cl_v2/TSMFTXH_move_v2(with legal moves complexity).csv",
}
dfs = [pd.read_csv(path) for path in files.values()]
dfs = [df.reset_index(drop=True) for df in dfs]
combined_df = pd.concat(dfs, axis=1)

# Step 2 : Drop duplicates and reorder the columns
df = combined_df.loc[:, ~combined_df.columns.duplicated()]
df = df.loc[:, ~df.T.duplicated()]
df = order_chess_columns(df)
df.rename(
    columns={df.columns[0]: "real_game_id", df.columns[1]: "game_id_dup"},
    inplace=True
)

if "game_id_dup" in df.columns:
    df = df.drop(columns=["game_id_dup"])
print("\nAfter removing duplicates:", df.shape)  # REVIEW validate if all non-duplicated columns are kept

# step 3 : Flatten and create variables
df["materials_on_board"] = df["materials_on_board"].apply(ast.literal_eval)
mat_df = df["materials_on_board"].apply(pd.Series).add_prefix("mat_")
df = pd.concat([df.drop(columns=["materials_on_board"]), mat_df], axis=1)

cols = ["neg","close(0-25)", "medium(26-50)", "far(51-100)", "mistakes(101-300)","blunders"]
for c in cols:
    df[c+"_prop"] = df[c] / df["legal_moves"]

chess1 = df.copy()
# step 4 : Sanity check - check if these columns are included in the csv
expected_groups = {
    "perspectives": [r'player_color', r'player_name', r'opp_color', r'opp_name'],  # from game_info
    "time_ratios": [r'time_ratio', r'(time_used|time_remaining|opp_time_remaining)'],  # adjust if needed
    "move_complexity": [r'legal_moves', r'neg', r'close.*', r'medium.*', r'far.*'],
    "count_materials": [r'material_difference', r'materials_on_board', r'pawn_islands', r'passed_pawns'],
    "tactics": [r'is_check', r'forks', r'absolute_pin', r'hanging_.*'],
    "forced_mate": [r'is_checkmate', r'moves?_to_mate']
}
for group, patterns in expected_groups.items():
    found = []
    for pat in patterns:
        found.extend([c for c in df.columns if re.search(pat, c, re.I)])
    if found:
        print(f"{group} columns found: {found}")
    else:
        print(f"{group} columns MISSING!")

# step 5 : Change categorical into numerical variables

# booleans → 0/1
bool_cols = chess1.select_dtypes(include=['bool']).columns
chess1[bool_cols] = chess1[bool_cols].astype('int8')

# column groups
onehot_cols = ['event','result','ECO','termination','clock_format',
               'player_color','opp_color','move_color']
direct_cols = ['moves_to_mate']
text_cols   = ['player_name','opp_name','opening','move','fen','real_game_id'] + [c for c in chess1.columns if 'best move' in c]

listed = pd.Index(onehot_cols + direct_cols + text_cols)
missing = listed.difference(chess1.columns)
if len(missing): print("Listed but not found:", list(missing)[:10])
all_cat = chess1.select_dtypes(include=['object','category','string']).columns

def encode_for_regression(df, onehot_cols, direct_cols, text_cols):
    df = df.copy()
    for c in [c for c in direct_cols if c in df.columns]:
        s = df[c].astype(str).str.strip().str.replace('M', '', regex=False)
        df[c] = pd.to_numeric(s, errors='coerce').astype('Int16')

    # 2) One-hot encode listed categorical (drop_first to avoid dummy trap)
    cats = [c for c in onehot_cols if c in df.columns]
    dummies = pd.get_dummies(df[cats].astype('category'),
                             prefix=cats, drop_first=True)

    # 3) Keep text columns as-is (pass-through)
    texts = df[[c for c in text_cols if c in df.columns]]

    # 4) Keep numeric pass-through (exclude source cat/text/direct columns)
    exclude = set(cats) | set(texts.columns) | set(direct_cols)
    passthru_num = df.select_dtypes(include=['number']).drop(columns=list(exclude), errors='ignore')

    # 5) Final matrix = numeric + converted direct_cols + dummies + text
    return pd.concat([passthru_num, df[[c for c in direct_cols if c in df.columns]], dummies, texts], axis=1)

# step 6 : Save the changes into new file
# X = encode_for_regression(chess1, onehot_cols, direct_cols, text_cols)
# X.to_csv("Hikaru_combined.csv", index=False, encoding="utf-8-sig")




