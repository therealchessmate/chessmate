from datetime import datetime
import pandas as pd

class Game:
    def __init__(self, id, start_dt_utc, platform, speed, opening, winner, moves, evaluations, time_spent, player_color):
        self.id = id
        self.start_dt_utc = start_dt_utc
        self.platform = platform
        self.speed = speed
        self.opening = opening
        self.winner = winner
        self.moves = moves
        self.evaluations = evaluations
        self.time_spent = time_spent
        self.player_color: str = player_color  # 'white' or 'black'


    def to_dataframe(self) -> pd.DataFrame:
        move_count = len(self.moves)

        def pad_or_trim(lst):
            if not lst:
                return [None] * move_count
            elif len(lst) < move_count:
                return lst + [None] * (move_count - len(lst))
            else:
                return lst[:move_count]

        return pd.DataFrame({
            "game_id": [self.id] * move_count,
            "move_number": list(range(1, move_count + 1)),
            "move": self.moves,
            "evaluation": pad_or_trim(self.evaluations),
            "time_spent": pad_or_trim(self.time_spent),
            "speed": [self.speed] * move_count,
            "platform": [self.platform] * move_count,
            "opening": [self.opening] * move_count,
            "winner": [self.winner] * move_count,
            "start_dt_utc": [self.start_dt_utc] * move_count,
        })


    def __repr__(self):
        return f"<Game {self.id} [{self.speed}] {self.start_dt_utc.date()} on {self.platform}>"
