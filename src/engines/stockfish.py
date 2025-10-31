from typing import List, Optional, Dict, Tuple
from engines.uci_engine import UCIEngine, Score
import chess, chess.pgn
from io import StringIO

class StockfishWrapper:
    def __init__(self, path_to_engine: str, depth: int = 12, threads: int = 1, hash_mb: int = 64):
        self.engine = UCIEngine(path_to_engine, options={"Threads": threads, "Hash": hash_mb})
        self.engine.start()
        self.depth = depth
        self.board: chess.Board  # track current board locally

    # ---------- position management ----------
    def load_startpos(self, clear_tt: bool = True) -> None:
        """Set engine and local state to the starting position."""
        if clear_tt: self.engine.ucinewgame()
        self.board = chess.Board()
        self.engine.position_startpos()

    def load_fen(self, fen: str, clear_tt: bool = True) -> None:
        """Set engine and local state from FEN."""
        if clear_tt: self.engine.ucinewgame()
        self.board = chess.Board(fen)
        self.engine.position_fen(fen)

    def set_moves_from_start(self, moves: List[str], clear_tt: bool = True) -> None:
        """Start from startpos and play a list of UCI moves, updating engine and local state."""
        if clear_tt: self.engine.ucinewgame()
        self.board = chess.Board()
        for mv in moves:
            self.board.push_uci(mv)
        # Send in one shot (faster) or send final FEN:
        self.engine.position_startpos(moves)

    def push_move(self, move_uci: str) -> None:
        """Append a single move to the current position (keeps TT)."""
        if self.board is None:
            # default to startpos if nothing loaded yet
            self.load_startpos(clear_tt=False)
        # Update local state
        self.board.push_uci(move_uci)
        # Update engine to the new FEN (simple & robust)
        self.engine.position_fen(self.board.fen())

    def current_fen(self) -> str:
        if self.board is None:
            # define a sensible default
            return chess.STARTING_FEN
        return self.board.fen()

    # ---------- evaluation ----------
    def get_evaluation(
        self,
        fen: Optional[str] = None,
        moves: Optional[List[str]] = None,
        depth: Optional[int] = None,
        clear_tt: bool = True,
    ) -> Dict[str, int | str]:
        """
        Evaluate a position using standard UCI (works with unpatched Stockfish).
        If fen/moves provided, loads that first. If neither provided and no
        position was loaded yet, uses startpos. Returns {'type': 'cp'|'mate', 'value': int}.
        """
        # Load position if caller provided one
        if fen is not None:
            self.load_fen(fen, clear_tt=clear_tt)
        elif moves is not None:
            self.set_moves_from_start(moves, clear_tt=clear_tt)
        elif self.board is None:
            # Nothing set yet → startpos
            self.load_startpos(clear_tt=clear_tt)
        # else: use whatever is currently in self.board / engine

        use_depth = depth if depth is not None else self.depth
        score, _ = self.engine.go_depth(use_depth)
        # Score is from side-to-move perspective (Stockfish convention)
        return {"type": score.kind, "value": score.value}

    def evaluate_position(self, fen: str) -> Dict[str, int | str]:
        """Convenience: evaluate a single FEN."""
        return self.get_evaluation(fen=fen, clear_tt=True)

    def evaluate_game(self, pgn_text: str) -> List[Tuple[str, Dict[str, int | str]]]:
        """
        Evaluate after each move of the PGN mainline.
        Keeps TT between moves (clear_tt=False) for speed.
        """
        game = chess.pgn.read_game(StringIO(pgn_text))
        if not game:
            return []
        self.load_startpos(clear_tt=True)
        out: List[Tuple[str, Dict[str, int | str]]] = []
        board = game.board()
        for mv in game.mainline_moves():
            san = board.san(mv)
            board.push(mv)
            # Keep local & engine state in sync incrementally
            self.board = board.copy()
            self.engine.position_fen(self.board.fen())
            score, _ = self.engine.go_depth(self.depth)
            out.append((san, {"type": score.kind, "value": score.value}))
        return out

    # Optional: works only after you patch C++
    def get_evaluation_breakdown(self, fen: Optional[str] = None) -> Optional[Dict]:
        if fen is not None:
            self.load_fen(fen, clear_tt=False)  # keep TT for speed
        return self.engine.eval_breakdown()
