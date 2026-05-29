from src.data_processing.parse_game import parse_game
from src.pipeline.run_pipeline import process_one_game, process_one_function, append_to_csv
from src.pipeline.safe import safe_process
import logging
import os
from multiprocessing import Pool
from functools import partial
from tqdm import tqdm

logging.basicConfig(
    filename = 'main.log',level = logging.INFO,
    format = '%(asctime)s %(levelname)s %(processName)s %(message)s'
)


def main():
    while True:
        batch_size = int(input("Enter Batch Size: "))
        player_username = input("Input player's username : ")
        file_txt = f"/Users/samuel/PycharmProjects/python-chess/data/raw_games/{player_username}_games.txt"
        if os.path.exists(file_txt):
            break
        print("Game file not found. Please enter a valid username.")
        logging.warning(f"Game file not found for {player_username}: {file_txt}")

    games = parse_game(file_txt)
    if not games:
        print(" Error. Cannot load game.")
        logging.error(f"Failed to parse games for {player_username}")
        return
    logging.info(f"Parsed {len(games)} games from {file_txt}")

    # --- Limit games if needed ---
    max_input = input("Number of games to process (press Enter for all): ").strip()
    max_games = int(max_input) if max_input else None
    games = games[:max_games]
    total_games = len(games)

    out_file = f"{player_username}_game_info.csv"  # TODO change output file name as desired -> manual change
    results_buffer = []

    # --- Process games in parallel ---
    with Pool(processes=8) as pool:
        # Review initialize engine path here, pass on to func
        func = partial(process_one_game, player_username=player_username)
        for i, game_result in enumerate(
                tqdm(pool.imap(partial(safe_process, func=func), games), total=total_games, desc="Processing games"),
                start=1):
            tqdm.write(f"Finished game {i}/{total_games}")
            results_buffer.extend(game_result)

            if i % batch_size == 0 or i == total_games:
                append_to_csv(results_buffer, out_file)
                logging.info(f"Saved batch ending at game {i}")
                results_buffer.clear()


if __name__ == "__main__":
    main()








