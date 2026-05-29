import chess
import chess.pgn


def analyze_other_position(game):
    board = game.board()
    move_list = []

    for node in game.mainline():
        color = board.turn
        move = node.move
        san_move = board.san(move)
        other_position_character = {
            'move' : san_move,
            'is_checkmate': is_checkmate_move(board, move),
            "player_kingside_castling_right" : board.has_kingside_castling_rights(color),  # check if the given side has castling rights
            "player_queenside_castling right" : board.has_queenside_castling_rights(color),
            "opp_kingside_castling_right" : board.has_kingside_castling_rights(not color),
            "opp_queenside_castling_right" : board.has_queenside_castling_rights(not color),
            # king is castled
            ** check_position_castling(board), # FIXME
            "passed_pawns": count_passed_pawns(board, color),
            # "isolated_pawns" : count-isolated_pawns
            "pawn_islands": count_pawn_islands(board, color),
            "doubled_pawn" : doubled_pawns(board, color),
            "connected_rooks" : find_connected_rooks(board, color),
            "bishop_pairs" : has_bishop_pair(board, color)
        }
        board.push(move)
        move_list.append(other_position_character)

    return move_list


def is_checkmate_move(board, move):
    board.push(move)
    is_mate = board.is_checkmate()
    board.pop()
    return is_mate


def check_position_castling(board): #FIXME
    return {
        "white_kingside_castle" : chess.Move.from_uci("e1g1") in board.legal_moves,
        "white_queenside_castle" : chess.Move.from_uci("e1c1") in board.legal_moves,
        "black_kingside_castle" : chess.Move.from_uci("e8g8") in board.legal_moves,
        "black_queenside_castle" : chess.Move.from_uci("e8c8") in board.legal_moves
    }


def count_passed_pawns(board, color): #FIXME
    """
    Count passed pawns and protected passed pawns for the given color.
    A passed pawn has no opposing pawns in front of it on the same or adjacent files.
    A protected passed pawn is a passed pawn defended by a friendly pawn on the adjacent file.
    """
    passed_pawns = 0
    direction = 1 if color == chess.WHITE else -1
    protected_passed_pawns = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.PAWN and piece.color == color:
            file = chess.square_file(square)
            rank = chess.square_rank(square)
            is_passed = True

            # check adjacent file and the ranks in front of pawns
            for f in [file-1, file, file + 1]:
                if 0 <= f <= 7:
                    for r in range(rank + direction, 8 if color == chess.WHITE else rank -1, -1):
                        sq = chess.square(f, r)
                        blocker = board.piece_at(sq)
                        if blocker and blocker.piece_type == chess.PAWN and blocker.color != color:
                            is_passed = False
                            break
            if is_passed:
                passed_pawns += 1

    return passed_pawns


def count_isolated_pawns(board, color): #FIXME
    isolated_pawns = 0
    pawn_files = []
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.PAWN and piece.color == color:
            file = int(chess.square_file(square))
            pawn_files.append(file)

    for f in pawn_files:
        if f-1 or f or f+1 not in pawn_files:
            isolated_pawns += 1

    return isolated_pawns


def count_pawn_islands(board, color):
    pawn_files = set()
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.PAWN and piece.color == color:
            pawn_files.add(chess.square_file(square))

    if not pawn_files:
        return 0

    sorted_files = sorted(pawn_files)
    islands = 1

    for i in range(1, len(sorted_files)):
        if sorted_files[i] - sorted_files[i - 1] > 1:
            islands += 1

    return islands


def find_connected_rooks(board, color) :
    """ Check if there are any piece between two rooks of the same color """
    rooks = [sq for sq in board.pieces(chess.ROOK, color)]
    connected = []
    if len(rooks) < 2:
        return False
    for i in range(len(rooks)):
        for j in range(i + 1, len(rooks)):
            sq1, sq2 = rooks[i], rooks[j]
            if chess.square_rank(sq1) == chess.square_rank(sq2):  # check all files and ranks between the two rook
                between = chess.SquareSet.between(sq1, sq2)
            elif chess.square_file(sq1) == chess.square_file(sq2):
                between = chess.SquareSet.between(sq1, sq2)
            else:
                continue
            if all(board.piece_at(sq) is None for sq in between):
                connected.append((sq1, sq2))
    return len(connected) == 1


def doubled_pawns(board, color):
    file_counts = [0] * 8  # count pawns in each file
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.PAWN and piece.color == color:
            file_counts[chess.square_file(square)] += 1

    doubled_pawns = sum(1 for count in file_counts if count >= 2)
    return doubled_pawns


def has_bishop_pair(board, color):
    """ Check if the player has both light and dark-squared bishops while the opponent doesn't have both"""
    my_bishops = [sq for sq in board.pieces(chess.BISHOP, color)]
    opp_bishops = [sq for sq in board.pieces(chess.BISHOP, not color)]
    square_colors = set((sq + chess.square_rank(sq)) % 2 for sq in my_bishops)
    opp_square_colors = set((sq + chess.square_rank(sq)) % 2 for sq in opp_bishops)
    if len(square_colors) == 2 and len(opp_square_colors) < 2:
        return True
    return False



