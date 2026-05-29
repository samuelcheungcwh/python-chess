import chess.pgn


def parse_game(file):
    """ this function reads game from pgn file and add each game to the game list"""
    game_list = []
    with open(file, 'r', encoding='utf-8') as f:
        while True:    # parse each game
            game = chess.pgn.read_game(f)
            if game is None:
                break
            game_list.append(game)

    return game_list


def normalize_username(name: str) -> str:
    return (name or "").strip().lower()

def resolve_perspective(white_name: str, black_name: str, player_username: str):
    w = normalize_username(white_name)
    b = normalize_username(black_name)
    me = normalize_username(player_username)

    if me == w:
        return {
            "player_color": "white",
            "player_name": white_name,
            "opp_name": black_name,
            "opp_color" : "black"
        }
    elif me == b:
        return {
            "player_color": "black",
            "player_name": black_name,
            "opp_name": white_name,
            "opp_color": "white"
        }

    return {
        "player_color": None,
        "player_name": None,
        "opp_color" : None,
        "opp_name": None
    }


def extract_game_info(game, player_username : str):
    game_info_dict = {}
    header_fields = [
        ("game_id", "GameId"),
        ("event", "Event"),
        ("clock_format", "TimeControl"),
        ("result", "Result"),
        ("opening", "Opening"),
        ("ECO", "ECO"),
        ("termination", "Termination")
    ]

    for key, header in header_fields:
        value = game.headers.get(header)
        if not value:  # if missing or empty
            value = "Unknown" if key == "result" else None
        game_info_dict[key] = value

    white_name = game.headers.get('White', '')
    black_name = game.headers.get('Black', '')
    white_elo = int(game.headers.get('WhiteElo', ''))
    black_elo = int(game.headers.get('BlackElo', ''))

    perspective = resolve_perspective(white_name, black_name, player_username)
    player_rating = white_elo if perspective['player_color'] == 'white' else (
        black_elo if perspective['player_color'] == 'black' else None)
    opp_rating = black_elo if perspective['player_color'] == 'white' else (
            white_elo if perspective['player_color'] == 'black' else None)

    game_info_dict.update({
        'total_half_moves': len(list(game.mainline_moves())),
        'player_color': perspective['player_color'],
        'player_name': perspective['player_name'],
        'player_rating': player_rating,
        'opp_color': perspective['opp_color'],
        'opp_name': perspective['opp_name'],
        'opp_rating': opp_rating,
        'rating_difference': abs(player_rating - opp_rating)
    })

    return game_info_dict





