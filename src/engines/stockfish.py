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
        pass

    def evaluate_position(self, fen: str) ->  List[Tuple[str, Optional[float]]]:
        pass
    