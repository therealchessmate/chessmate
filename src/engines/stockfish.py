# engines/stockfish_wrapper.py
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
import chess, chess.pgn
from io import StringIO

from engines.uci_engine import UCIEngine, Score

@dataclass(frozen=True)
class EvalConfig:
    depth: int = 12
    clear_tt: bool = True   # send 'ucinewgame' before unrelated positions
    perspective: str = "stm"  # "stm" or "white"

class StockfishWrapper:
    """
    Domain-level helpers on top of UCIEngine.
    All evaluation methods share one shape and return a Score dataclass.
    """

    def __init__(self, path_to_engine: str, depth: int = 12, threads: int = 1, hash_mb: int = 64):
        self.engine = UCIEngine(path_to_engine, options={"Threads": threads, "Hash": hash_mb})
        self.engine.start()
        self.cfg = EvalConfig(depth=depth)
        self._has_position = False

    # --- lifecycle ---
    def close(self): self.engine.stop()
    def set_depth(self, depth: int): self.cfg = EvalConfig(depth=depth, clear_tt=self.cfg.clear_tt, perspective=self.cfg.perspective)
    def set_threads(self, n: int): self.engine.setoption("Threads", n)
    def set_perspective(self, mode: str):  # "stm" or "white"
        if mode not in ("stm", "white"): raise ValueError("perspective must be 'stm' or 'white'")
        self.cfg = EvalConfig(depth=self.cfg.depth, clear_tt=self.cfg.clear_tt, perspective=mode)

    # --- shared internals ---
    def _ensure_position(self, fen: Optional[str], moves: Optional[List[str]], clear_tt: bool) -> None:
        """Set FEN or startpos+moves. If neither is given and nothing loaded, set startpos."""
        if fen:
            if clear_tt: self.engine.ucinewgame()
            self.engine.position_fen(fen)
            self._has_position = True
            return
        if moves:
            if clear_tt: self.engine.ucinewgame()
            self.engine.position_startpos(moves)
            self._has_position = True
            return
        if not self._has_position:
            if clear_tt: self.engine.ucinewgame()
            self.engine.position_startpos()
            self._has_position = True

    @staticmethod
    def _flip_to_white(score: Score, side_to_move_is_white: bool) -> Score:
        if side_to_move_is_white or score.kind == "mate":
            return score
        # Flip cp to white’s perspective
        return Score(score.kind, -score.value)

    # --- public API (uniform shape) ---
    def get_evaluation(
        self,
        fen: Optional[str] = None,
        moves: Optional[List[str]] = None,
        depth: Optional[int] = None,
        clear_tt: bool = True,
    ) -> Score:
        """
        Evaluate a position.
        - If `fen` is provided: sets that FEN (clears TT by default) and evaluates.
        - Else if `moves` is provided: starts from startpos, plays moves, evaluates.
        - Else: if no position set yet, evaluates startpos; otherwise evaluates current engine position.
        Returns: Score(kind="cp"|"mate", value=int) from side-to-move perspective or white (configurable).
        """
        self._ensure_position(fen, moves, clear_tt)
        use_depth = depth if depth is not None else self.cfg.depth
        score, _ = self.engine.go_depth(use_depth)

        if self.cfg.perspective == "white":
            # Determine side to move from the provided FEN or the last move list
            stm_white = True
            if fen:
                try:
                    stm_white = (fen.split()[1] == "w")
                except Exception:
                    stm_white = True
            elif moves:
                # startpos + even number of moves => black to move
                stm_white = (len(moves) % 2 == 0)
            # else: unknown; default to white
            score = self._flip_to_white(score, stm_white)

        return score

    def evaluate_position(self, fen: str, depth: Optional[int] = None, clear_tt: bool = True) -> Score:
        """Thin alias: evaluate a single FEN."""
        return self.get_evaluation(fen=fen, depth=depth, clear_tt=clear_tt)

    def evaluate_game(self, pgn_text: str, per_move: bool = True, depth: Optional[int] = None) -> List[Tuple[str, Score]]:
        """
        Evaluate a PGN mainline. If per_move=True, returns a list [(SAN, Score after move), ...].
        """
        game = chess.pgn.read_game(StringIO(pgn_text))
        if not game:
            return []
        board = game.board()
        results: List[Tuple[str, Score]] = []
        for mv in game.mainline_moves():
            san = board.san(mv)
            board.push(mv)
            s = self.get_evaluation(fen=board.fen(), depth=depth if depth is not None else self.cfg.depth, clear_tt=False)
            results.append((san, s))
        return results

    # Optional—works only if your engine implements 'eval_breakdown'
    def get_evaluation_breakdown(self, fen: Optional[str] = None, clear_tt: bool = False) -> Optional[Dict]:
        """
        If fen provided, set it first (no TT clear by default to keep caches).
        Returns a dict like {"mobility":..., "pawns":..., "total":...} or None if engine doesn't support it.
        """
        if fen:
            self._ensure_position(fen, None, clear_tt)
        return self.engine.eval_breakdown()
