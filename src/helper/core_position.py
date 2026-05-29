import chess
import chess.pgn
import chess.engine
from src.config.config import ENGINE_PATH, ENGINE_CONFIG

def analyze_core_position(game) -> list[dict]:
    """ This module returns (10) key tactical characteristics for each position. """
    board = game.board()
    move_list = []

    # FIXME set path as relative, use get_wd()
    with chess.engine.SimpleEngine.popen_uci(str(ENGINE_PATH)) as engine:

        for node in game.mainline():
            color = board.turn
            move = node.move
            position_character = {
                'legal_moves': len(list(board.legal_moves)),
                'captures': sum(1 for m in board.legal_moves if board.is_capture(m)),
                'checks' : sum(1 for m in board.legal_moves if board.gives_check(m)),
                'is_check' : board.is_check(),
                'promotions' : sum(1 for m in board.legal_moves if m.promotion is not None),
                'absolute_pin' : count_absolute_pin(board, color),
                # 'relative pin' : count_relative_pin(board, color), #Review
                'forks' : count_forks(board, color), #Review
                'moves_to_mate' : detect_checkmate(board, engine)
                # forcing sequence
                    # follows the logic of count_hanging_pieces -> attackers > defenders)
            }
            position_character |= capture_by_types(board)
            position_character |= count_hanging_pieces(board, color)
            move_list.append(position_character)
            board.push(move)

    return move_list


def capture_by_types(board) -> dict[str, int]:
    """ count potential captured pieces by their type """
    capture_types = {'capture_pawns': 0, 'capture_minor_pieces': 0, 'capture_rooks': 0, 'capture_queens': 0}

    for m in board.legal_moves:
        if board.is_capture(m):
            captured_piece_sq = board.piece_at(m.to_square)
            if captured_piece_sq:
                piece_type = captured_piece_sq.piece_type
                if piece_type == 1:
                    capture_types['capture_pawns'] += 1
                elif piece_type == 2 or piece_type == 3:
                    capture_types['capture_minor_pieces'] += 1
                elif piece_type == 4:
                    capture_types['capture_rooks'] += 1
                elif piece_type == 5:
                    capture_types['capture_queens'] += 1

    return capture_types


def count_absolute_pin(board, color):
    """
    Count number of own pieces_being pinned to the king of own colore
    """
    pinned = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == color:
            if board.is_pinned(color, square):
                pinned += 1

    return pinned


def count_relative_pin(board, color): # FIXME
    """ count pieces pinned to major piece"""
    count = 0
    opp_color = not color
    valuable_pieces = [chess.QUEEN, chess.ROOK]

    # find own queen and rooks
    for square in chess.SQUARES:
        target = board.piece_at(square)
        if not target or target.color != color or target.piece_type not in valuable_pieces :
            continue

        board.remove_piece_at(target)

    # iterate all pieces -> see if removing them would expose valuable pieces being attacked -> count +=1

    return count


def count_forks(board, color):  # FIXME
    """ Count move that attacks two or more pieces simultaneously, regardless if those pieces are defended """
    forks = 0

    for m in board.legal_moves:
        piece = board.piece_at(m.from_square)
        if not piece or piece.color != color:
            continue

        board.push(m)
        attacked_squares = board.attacks(m.to_square)
        attacked_pieces = sum(1 for sq in attacked_squares
                              if board.piece_at(sq) and board.piece_at(sq).color != color)
        board.pop()

        if attacked_pieces >= 2:
            forks += 1

    return forks


def is_hanging(board, square, color):
    opp_color = not color
    if not board.is_attacked_by(opp_color, square):
        return False
    if board.is_attacked_by(color, square):
        return False
    return True


def count_hanging_pieces(board, color) -> dict[str, int]: #FIXME
    """Count pieces that are attacked but not defended"""
    hanging_count = {'hanging_pawns': 0, 'hanging_minor_pieces': 0, 'hanging_rooks': 0, 'hanging_queen': 0}

    for square in board.pieces(chess.PAWN, color):
        if is_hanging(board, square, color):
            hanging_count['hanging_pawns'] += 1

    for square in board.pieces(chess.BISHOP, color):
        if is_hanging(board, square, color):
            hanging_count['hanging_minor_pieces'] += 1

    for square in board.pieces(chess.KNIGHT, color):
        if is_hanging(board, square, color):
            hanging_count['hanging_minor_pieces'] += 1

    for square in board.pieces(chess.ROOK, color):
        if is_hanging(board, square, color):
            hanging_count['hanging_rooks'] += 1

    for square in board.pieces(chess.QUEEN, color):
        if is_hanging(board, square, color):
            hanging_count['hanging_queen'] += 1

    return hanging_count


def detect_checkmate(board, engine): # FIXME
    """  Detect mate-in-1 to mate-in-4+ from the current board position using the chess engine. """
    result = engine.analyse(board, chess.engine.Limit(depth=15))
    score = result["score"]
    if score.is_mate():
        mate_in = score.relative.mate()
        mate_steps = abs(mate_in)

        if mate_in > 0:
            if mate_steps == 1:
                return "M1"
            elif mate_steps == 2:
                return "M2"
            elif mate_steps == 3:
                return "M3"
            elif mate_steps >= 4:
                return "M4+"
        else:
            if mate_steps == 1:
                return "-M1"
            elif mate_steps == 2:
                return "-M2"
            elif mate_steps == 3:
                return "-M3"
            elif mate_steps >= 4:
                return "-M4+"
    return None
