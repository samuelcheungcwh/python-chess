from contextlib import nullcontext

import chess.pgn
import io
import inspect
from src.data_processing.parse_game import *
from src.data_processing.extract_move_and_time import *
from src.helper.core_position import *
from src.helper.other_position import *
from src.helper.position_evaluation import *
from src.config.config import *
import time
from pprint import pprint

own_game = '''
[Event "rated rapid game"]
[Site "https://lichess.org/8nxMqpXV"]
[Date "2021.10.04"]
[White "GuiMundstock"]
[Black "cream193"]
[Result "0-1"]
[GameId "8nxMqpXV"]
[UTCDate "2021.10.04"]
[UTCTime "14:52:15"]
[WhiteElo "1328"]
[BlackElo "1314"]
[WhiteRatingDiff "-19"]
[BlackRatingDiff "+49"]
[Variant "Standard"]
[TimeControl "600+0"]
[ECO "A00"]
[Opening "Barnes Opening"]
[Termination "Time forfeit"]

1. f3 { [%clk 0:10:00] } 1... d5 { [%clk 0:10:00] } 2. g4 { [%clk 0:09:55] } 2... e5 { [%clk 0:09:59] } 3. Nh3 { [%clk 0:09:51] } 3... Nc6 { [%clk 0:09:44] } 4. Bg2 { [%clk 0:09:51] } 4... f5 { [%clk 0:09:38] } 5. Kf2 { [%clk 0:09:46] } 5... fxg4 { [%clk 0:09:37] } 6. d4 { [%clk 0:09:41] } 6... gxh3 { [%clk 0:09:29] } 7. f4 { [%clk 0:09:21] } 7... hxg2 { [%clk 0:09:26] } 8. f5 { [%clk 0:08:45] } 8... gxh1=Q { [%clk 0:09:23] } 9. h4 { [%clk 0:08:39] } 9... Qxd1 { [%clk 0:09:21] } 10. e4 { [%clk 0:08:35] } 10... Qxh4+ { [%clk 0:09:20] } 0-1
'''

sample_pgn = '''
[Event "Sample Game"]
[Site "Lichess"]
[Date "2023.03.01"]
[Round "-"]
[White "SampleWhite"]
[Black "SampleBlack"]
[Result "1-0"]
[TimeControl "600+0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 
4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 
7. Bb3 d6 8. c3 O-O 9. h3 Nb8 
10. d4 Nbd7 11. Nbd2 Bb7 12. Bc2 Re8 
13. Nf1 Bf8 14. Ng3 g6 15. a4 c5 
16. d5 c4 17. Bg5 h6 18. Be3 Qc7 
19. Qd2 Kh7 20. Nh2 Nc5 21. Rf1 Bg7 
22. f4 exf4 23. Rxf4 Re7 24. Raf1 Ng8 
25. Bd4 Bxd4+ 26. Qxd4 Rf8 27. Ng4 Nd7 
28. Nf5 gxf5 29. Rxf5 Qc5 30. e5 Qxd4+ 
31. cxd4 Kg7 32. Nf6 dxe5 33. d6 Re6 
34. Nxd7 Rxd6 35. Nxf8 Kxf8 36. Rxf7+ Ke8 
37. Rxb7 Rxd4 38. Bg6+ Kd8 39. Rf8# 1-0 
'''

anderssens_mate = '''
[Event "Anderssen's Mate"]
[Site "Test"]
[Date "2025.08.02"]
[Round "?"]
[White "Player1"]
[Black "Player2"]
[WhiteElo "1234"]
[BlackElo "1534"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. b4 Bxb4 5. c3 Ba5 6. d4 exd4 7. O-O d3 8. Qb3 Qe7 9. Ba3 d6 10. e5 Nh6 11. exd6 cxd6 12. Re1 Ne5 
13. Nxe5 dxe5 14. Bxe7 Kxe7 15. Rxe5+ Be6 16. Rxa5 b6 17. Qa3+ Kd7 18. Bb5+ Kc7 19. Rxa7+ Kb8 20. Ra8+ Kc7 21. Qe7+ Bd7 22. Qxd7# 1-0

'''


def test_helper(pgn_text, func):
    """  Test function that passes on game """
    start = time.time()
    pgn_io = io.StringIO(pgn_text)
    game = chess.pgn.read_game(pgn_io)
    result = func(game)
    pprint(result)

    print(time.time() - start)


def test_function(pgn_text, func):
    """ Test function that passes on move """
    pgn_io = io.StringIO(pgn_text)
    game = chess.pgn.read_game(pgn_io)
    board = game.board()
    move_number = 0

    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())

    need_engine = 'engine' in param_names

    engine_context = (
        chess.engine.SimpleEngine.popen_uci(str(ENGINE_PATH))
        if need_engine
        else nullcontext()
    )

    with engine_context as engine:
        if need_engine:
            engine.configure({"Threads": 1, "Hash": 64})

        start = time.time()
        for i, node in enumerate(game.mainline()):
            color = board.turn
            move = node.move
            if board.turn == chess.WHITE:
                move_number += 1

            kwargs = {}
            if 'board' in param_names: kwargs['board'] = board
            if 'move' in param_names: kwargs['move'] = move
            if 'color' in param_names: kwargs['color'] = color
            if 'engine' in param_names: kwargs['engine'] = engine

            result = func(**kwargs)
            pprint(f"{move_number}: {board.san(move)} → {result}")
            board.push(move)

        print(f"Time: {time.time() - start:.2f}s")


test_helper(own_game, position_evaluation)
