from typing import List, Tuple, Optional

class EvaluationDropDetector:
    def __init__(self, threshold_cp: int = 100):
        """
        :param threshold_cp: Minimum drop in centipawns to consider significant.
        """
        self.threshold_cp = threshold_cp

    def _normalize_eval(self, eval_str: str) -> Optional[float]:
        """
        Converts evaluation string (e.g., "+0.53", "-M3") to numeric score.
        Mates are normalized to +/- 1000 for detection purposes.
        """
        if eval_str.startswith('M') or eval_str.startswith('+M') or eval_str.startswith('-M'):
            return 1000 if eval_str.startswith('+') else -1000
        try:
            return float(eval_str)
        except ValueError:
            return None

    def find_drops(
        self,
        evaluations: List[str],
        positions: List[str]
    ) -> List[Tuple[int, float, float, str]]:
        """
        Finds evaluation drops over the threshold and returns:
        - index,
        - evaluation before,
        - evaluation after,
        - FEN at the drop.

        :param evaluations: List of evaluation strings (e.g. "+0.53", "-1.20", "+M2").
        :param positions: List of FEN strings or PGN moves.
        :return: List of tuples with (index, eval_before, eval_after, fen_at_drop)
        """
        assert len(evaluations) == len(positions), "Evaluations and positions must match in length."

        drops = []
        for i in range(1, len(evaluations)):
            prev_eval = self._normalize_eval(evaluations[i - 1])
            curr_eval = self._normalize_eval(evaluations[i])

            if prev_eval is None or curr_eval is None:
                continue

            drop = prev_eval - curr_eval
            if drop >= self.threshold_cp:
                drops.append((i, prev_eval, curr_eval, positions[i]))

        return drops
