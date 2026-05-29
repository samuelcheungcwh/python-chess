import chess.pgn


def parse_clk_time_to_seconds(hms):
    """Parse clock comment [%clk 0:01:00]"""
    clk_time = hms.split("[%clk")[1].rsplit("]")[0]
    parts = clk_time.split(":")
    total_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return total_seconds


def time_ratios(color, remaining_time, time_used):

    def safe_div(num, den):
        return round(num / den, 2) if den > 0 else None

    return {
        "player_remaining_time/opp_remaining_time": safe_div(remaining_time[color],
                                                             remaining_time[not color]),
        "opp_remaining_time/player_remaining_time": safe_div(remaining_time[not color],
                                                             remaining_time[color]),
        "time_used/remaining_time": safe_div(time_used, remaining_time[color]),
    }


def extract_moves_and_time(game, ctx = None):
    """Extract time-related variables and move information."""
    init_time = 0
    for n in game.mainline():  # FIXME pass global initial time instead
        first_clk = parse_clk_time_to_seconds(n.comment)
        if first_clk is not None:
            init_time = first_clk
            break

    board = game.board()
    moves_list = []
    time_remaining = {chess.WHITE: init_time, chess.BLACK: init_time}
    prev_remaining_time = {chess.WHITE: init_time, chess.BLACK: init_time}
    prev_time_used = {chess.WHITE: 0, chess.BLACK: 0}

    for node in game.mainline():
        move = board.san(node.move)
        move_number = board.fullmove_number
        fen = board.fen()
        clk_time = node.comment

        color = board.turn
        opp_color = not color
        current = parse_clk_time_to_seconds(clk_time)  # remaining time after the move

        if current is not None:
            time_used = max(0, prev_remaining_time[color] - current)
            time_remaining[color] = current # remaining time after move
        else:
            time_used = 0


        # update time remaining for the color
        prev_remaining_time[color] = time_remaining[color]
        time_metrics = time_ratios(color, time_remaining, time_used)

        moves_list.append({
            'move_number': move_number,
            'move': move,
            'fen' : fen,
            'move_color': 'White' if color == chess.WHITE else 'Black',
            'time_used' : time_used,
            'time_remaining' : time_remaining[color],
            'opp_time_remaining' : time_remaining[opp_color],
            'prev_time_remaining' : prev_remaining_time[color],
            'opp_prev_time_remaining' : prev_remaining_time[opp_color],
            'prev_time_used': prev_time_used[color],
            'opp_prev_time_used' : prev_time_used[opp_color],
            ** time_metrics
        })

        board.push(node.move)
        prev_time_used[color] = time_used
        time_remaining[color] = prev_remaining_time[color]

    return moves_list



