from src.data_processing.parse_game import parse_game

def count_moves(games):
    """ Count total observation of moves for a player """
    total_moves = 0
    for game in games:
        for _ in game.mainline():
            total_moves += 1
    return total_moves

players = [
    ("DaniduChess", 1000),
    ("octavia", 1500),
    ("timothyarm", 2000),
    ("Dmitry_Kornilovich", 2500),
    ("TSMFTXH", 3000),
]

for name, rating in players:
    file_txt = f"/Users/samuel/PycharmProjects/python-chess/data/raw_games/{name}_games.txt"
    player_games = parse_game(file_txt)
    player_moves = count_moves(player_games)
    print(f"{name}({rating}) : {len(player_games)} games, {player_moves} moves")