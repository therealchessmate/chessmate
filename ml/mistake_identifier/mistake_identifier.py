import chess
import chess.engine
import pandas as pd
from typing import List, Dict, Any, Tuple


class MistakeIdentifier:
    """
    Identifies the type of mistake based on centipawn loss and comparison
    with the best Stockfish move.
    """

    def __init__(self, engine_path: str = "stockfish", depth: int = 18) -> None:
        self.engine_path = engine_path
        self.depth = depth
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    def classify_mistake(self, actual_eval: float, best_eval: float, time_used: float) -> str:
        """
        Classifies the mistake based on evaluation difference and time used.

        Returns:
            str: Type of mistake
        """
        cp_loss = best_eval - actual_eval
        abs_loss = abs(cp_loss)

        if time_used < 2 and abs_loss > 150:
            return "Time trouble"
        if abs_loss > 300:
            return "Blunder"
        elif abs_loss > 150:
            return "Mistake"
        elif abs_loss > 50:
            return "Inaccuracy"
        else:
            return "Minor inaccuracy or stylistic"

    def analyze_position(self, fen: str, actual_move_uci: str, time_used: float) -> Dict[str, Any]:
        board = chess.Board(fen)
        actual_move = chess.Move.from_uci(actual_move_uci)

        # Evaluate current position
        info_best = self.engine.analyse(board, chess.engine.Limit(depth=self.depth))
        best_move = info_best["pv"][0]
        best_eval = self._score_to_cp(info_best["score"])

        # Apply actual move
        board.push(actual_move)
        info_actual = self.engine.analyse(board, chess.engine.Limit(depth=self.depth))
        actual_eval = self._score_to_cp(info_actual["score"])

        mistake_type = self.classify_mistake(actual_eval, best_eval, time_used)

        return {
            "fen": fen,
            "best_move": best_move.uci(),
            "actual_move": actual_move.uci(),
            "best_eval_cp": best_eval,
            "actual_eval_cp": actual_eval,
            "cp_loss": best_eval - actual_eval,
            "mistake_type": mistake_type,
            "time_used": time_used
        }

    def analyze_multiple(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Expects a DataFrame with:
        - fen
        - actual_move (in UCI)
        - time_used (in seconds)

        Returns the same DataFrame with classified mistake types.
        """
        results = []
        for _, row in df.iterrows():
            result = self.analyze_position(
                fen=row["fen"],
                actual_move_uci=row["actual_move"],
                time_used=row.get("time_used", 0.0)
            )
            results.append(result)
        return pd.DataFrame(results)

    def _score_to_cp(self, score) -> float:
        """Convert score to centipawn float."""
        if score.is_mate():
            # Treat mate in N as +-1000 to 3000 centipawns
            mate = score.mate()
            return 3000 if mate > 0 else -3000
        return score.score()

    def close(self) -> None:
        self.engine.quit()