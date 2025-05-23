from stockfish import Stockfish
import chess.pgn
from io import StringIO
from typing import List, Tuple, Optional

class StockfishWrapper:
    def __init__(self, path_to_engine: str, depth: int = 15, threads: int = 1):
        self.engine = Stockfish(path=path_to_engine, depth=depth, parameters={"Threads": threads})

    def evaluate_game(self, pgn_text: str) -> List[Tuple[str, Optional[float]]]:
        """
        Evaluate PGN game and return (move_san, evaluation_in_centipawns)
        """
        pgn_io = StringIO(pgn_text)
        game = chess.pgn.read_game(pgn_io)
        board = game.board()
        evaluations = []

        for move in game.mainline_moves():
            board.push(move)
            self.engine.set_fen_position(board.fen())
            eval_ = self.engine.get_evaluation()

            if eval_["type"] == "cp":
                evaluations.append((board.san(move), eval_["value"] / 100))  # convert to pawn units
            elif eval_["type"] == "mate":
                evaluations.append((board.san(move), f"# {eval_['value']}"))
            else:
                evaluations.append((board.san(move), None))

        return evaluations
