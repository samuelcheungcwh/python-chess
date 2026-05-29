import chess
import chess.pgn
import chess.engine
import time
from src.config.config import ENGINE_PATH


def position_evaluation(game) -> list[dict]:
    """ Evaluate position value with stockfish engine """
    board = game.board()
    move_list = []

    with chess.engine.SimpleEngine.popen_uci(str(ENGINE_PATH)) as engine:

        for node in game.mainline():
            color = board.turn
            move = node.move

            centipawn_loss = stockfish_evaluation(board, move, color, engine)
            evaluation = {'material_difference' : material_difference(board, color), }
            evaluation |= count_materials_both_side(board, color)
            evaluation |= legal_moves_complexity(board,color,engine)
            evaluation |= centipawn_loss
            move_list.append(evaluation)
            board.push(move)

        return move_list


def material_difference(board, color):
    """Calculate material difference in terms of points from the player's perspective."""
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }

    white_material = 0
    black_material = 0

    for piece in board.piece_map().values():
        value = piece_values[piece.piece_type]
        if piece.color == chess.WHITE:
            white_material += value
        else:
            black_material += value

    if color == chess.WHITE:
        return white_material - black_material
    else:
        return black_material - white_material


def count_materials_both_side(board,color):
    piece_names = {
        chess.PAWN: "pawn",
        chess.KNIGHT: "knight",
        chess.BISHOP: "bishop",
        chess.ROOK: "rook",
        chess.QUEEN: "queen",
        chess.KING: "king"
    }

    materials = {
        f"{color_name}_{name}": len(board.pieces(ptype, color))
        for color, color_name in [(chess.WHITE, "white"), (chess.BLACK, "black")]
        for ptype, name in piece_names.items()
    }

    return materials


def legal_moves_complexity(board, color, engine):
    """ categorize all legal moves as close to, not too close to, and far from the best move by engine """
    legal_moves = list(board.legal_moves)

    categories = {
        'neg_alt': 0,
        'close_alt': 0,
        'medium_alt': 0,
        'far_alt': 0,
        'mistake_alt': 0,
        'blunder_alt': 0
    }

    info = engine.analyse(
        board,
        chess.engine.Limit(depth=15),
        multipv=len(legal_moves),
        root_moves=legal_moves
    )

    best_score = info[0]["score"].pov(color).score(mate_score=10000)

    for idx, move in enumerate(info):
        move_score = info[idx]["score"].pov(color).score(mate_score=10000)
        score_diff = best_score - move_score

        if score_diff < 0:
            categories['neg_alt'] += 1
        elif score_diff <= 25:
            categories['close_alt'] += 1
        elif 25 < score_diff <= 50:
            categories['medium_alt'] += 1
        elif 50 < score_diff <= 100:
            categories['far_alt'] += 1
        elif 100 < score_diff <= 300:
            categories['mistake_alt'] += 1
        else:
            categories['blunder_alt'] += 1

    return categories


def stockfish_evaluation(board, move, color, engine):
    """
    Evaluate best move vs actual move from the same initial position.
    Centipawn Loss = eval(best move position) - eval(actual move position)
    """
    depths = [1, 2, 3, 7, 11, 15]
    engine_evaluation = {}

    for depth in depths:
        start = time.time()
        # Get best move from current position
        best_result = engine.play(board, chess.engine.Limit(depth=depth))
        best_move = best_result.move

        # Score position after best move
        best_board = board.copy(stack = False)
        best_board.push(best_move)
        best_score = engine.analyse(best_board, chess.engine.Limit(depth=depth))["score"].pov(color).score(
            mate_score=10000)

        # Score position after actual move
        actual_board = board.copy(stack = False)
        actual_board.push(move)
        actual_score = engine.analyse(actual_board, chess.engine.Limit(depth=depth))["score"].pov(color).score(
            mate_score=10000)

        # Centipawn loss
        engine_evaluation[f"depth{depth}_best_move"] = board.san(best_move)
        engine_evaluation[f"depth{depth}"] = best_score - actual_score
        if time.time() - start > 180:
            print(f"Evaluation took {time.time() - start} seconds")
            continue

    return engine_evaluation


# input a txt and parse games
# input a game pgn for this
# put a board for each move to stockfish evaluation -> return evaluation {}
