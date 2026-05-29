from extract_game_data import extract_raw_data, save_to_file


### FIXME Rename this program ; Save the txt file in data/ raw_games
def save_all_games():
    """ Download game data in txt format by player's name"""
    username = input("Player's username: ")
    game_type = input("Chosen game type (bullet, blitz, rapid...): ")
    max_games = int(input("How many games to analyze: "))
    file = extract_raw_data(username, game_type, max_games)
    save_to_file(file, username)

if __name__ == "__main__":
    save_all_games()
