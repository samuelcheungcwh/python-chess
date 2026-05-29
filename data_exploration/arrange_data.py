import re
import pandas as pd

def order_chess_columns(df: pd.DataFrame):
    """Reorder columns in a chess dataset into logical groups."""
    cols = list(df.columns)
    pick = lambda pat: [c for c in cols if re.search(pat, c, re.I)]

    ordered = []
    ordered += pick(r'^(game_?id|event|site|date|result|termination|variant|time[_ ]?control|clock|opening|eco|rated|rating_group|total_half_moves)$')
    ordered += pick(r'(^white($|_)|^black($|_)|player(_|$)|opp(_|$)|player_.*rating|opp_.*rating|rating_difference)')
    ordered += pick(r'^(move_number|ply|move$|fen|move_color)$')
    ordered += pick(r'(time_used|prev_time_used|time_remaining|opp_time_remaining|player_remaining_time|opp_remaining_time|clock|remaining|_s)')
    ordered += pick(r'(material_difference|materials_on_board|pawn_islands|passed_pawns|doubled_pawn|connected_rooks|bishop_pairs|'
                    r'captures?|capture_(pawns|minor_pieces|rooks|queens)|checks?|is_check|is_checkmate|moves?_to_mate|promotions?|'
                    r'absolute_pin|forks|hanging_(pawns|minor_pieces|rooks|queen)|castl|kingside|queenside)')
    ordered += pick(r'^depth\d+\s*best move$|^depth\d+(_v2)?$')
    ordered += pick(r'^(legal_moves|neg|close.*|medium.*|far.*|mistakes.*|blunders)$')

    # Append leftovers at the end, remove duplicates while preserving order
    ordered = list(dict.fromkeys(ordered + [c for c in cols if c not in ordered]))

    return df[ordered]