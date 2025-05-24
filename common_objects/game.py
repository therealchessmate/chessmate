from datetime import datetime
import pandas as pd

class Game:
    def __init__(self,
                 id: str,
                 start_dt_utc: datetime,
                 platform: str,
                 speed: str,
                 opening: str,
                 status: str,
                 winner: str,
                 moves: list[str],
                 evaluations: list[float] = None,
                 time_spent: list[float] = None):
        self.id = id
        self.start_dt_utc = start_dt_utc
        self.platform = platform
        self.speed = speed
        self.opening = opening
        self.status = status
        self.winner = winner
        self.moves = moves
        self.evaluations = evaluations or []
        self.time_spent = time_spent or []

    def to_dataframe(self) -> pd.DataFrame:
        move_count = len(self.moves)
        return pd.DataFrame({
            "game_id": [self.id] * move_count,
            "move_number": list(range(1, move_count + 1)),
            "move": self.moves,
            "evaluation": self.evaluations if self.evaluations else [None] * move_count,
            "time_spent": self.time_spent if self.time_spent else [None] * move_count,
            "speed": [self.speed] * move_count,
            "platform": [self.platform] * move_count,
            "opening": [self.opening] * move_count,
            "status": [self.status] * move_count,
            "winner": [self.winner] * move_count,
            "start_dt_utc": [self.start_dt_utc] * move_count,
        })

    def __repr__(self):
        return f"<Game {self.id} [{self.speed}] {self.start_dt_utc.date()} on {self.platform}>"
