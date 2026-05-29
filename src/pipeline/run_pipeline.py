from src.data_processing.parse_game import extract_game_info
from src.data_processing.extract_move_and_time import extract_moves_and_time
from src.helper.core_position import analyze_core_position
from src.helper.other_position import analyze_other_position
from src.helper.position_evaluation import position_evaluation, stockfish_evaluation
import pandas as pd
import os
import chess
from src.config.config import ENGINE_PATH


OUT_DIR = "data"
def append_to_csv(data, filename):
    if not data:
        return
    os.makedirs(OUT_DIR, exist_ok=True)

    filepath = os.path.join(OUT_DIR, filename)
    df = pd.DataFrame(data)
    header = not os.path.exists(filepath)
    df.to_csv(filepath, mode='a', header=header, index=False)


def process_one_game(game, player_username):
    """ Process all variables of a single game"""
    game_info = extract_game_info(game, player_username = player_username)
    move_data = extract_moves_and_time(game)
    core_position = analyze_core_position(game)
    other_position = analyze_other_position(game)
    stockfish_eval = position_evaluation(game)

    # Broadcast game-level info to all moves.
    for move in move_data:
        move.update(game_info)


    combined = [{**m, **t, **o, **s}
                for m, t, o,s in zip(move_data, core_position, other_position, stockfish_eval) # s, stockfish_eval
    ]

    return combined




#TODO appending individual function
def process_one_function(game, player_username):
    """ Append individual function to existing move summary"""
    try :
        board = game.board()
        move_list = []
        with chess.engine.SimpleEngine.popen_uci(str(ENGINE_PATH)) as engine:

            for node in game.mainline():
                color = board.turn
                move = node.move
                evaluation = {}

                centipawn_loss = stockfish_evaluation(board, move, color, engine)
                evaluation |= centipawn_loss
                move_list.append(evaluation)
                board.push(move)

            return move_list

    except Exception as e:
        print(f"Error processing game : {e}")
        return []