import requests


def extract_raw_data(username, game_type, max_games):
    """ extract data for one player using Lichess API """
    url = f"https://lichess.org/api/games/user/{username}"
    params = {
        "perfType": game_type,  # Select relevant parameters for game information
        "max": max_games,
        "clocks": "true",
        "evals": "false",
        "opening": "true",
        "pgnInJson": "true"
    }
    headers = {"Accept": "application/x-chess-pgn"}  # return PGN format
    response = requests.get(url, params=params, headers=headers)
    return response.text


def save_to_file(game, username):
    """ write chess games in local file """
    filename = f"{username}_games.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(game)
    print(f"Saved {filename}")

