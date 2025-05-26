from common_objects.game import Game  
import pandas as pd

class Player:
    def __init__(self, username: str):
        self.username = username
        self.ultraBullet: dict[str, Game] = {}
        self.bullet: dict[str, Game] = {}
        self.blitz: dict[str, Game] = {}
        self.rapid: dict[str, Game] = {}
        self.classical: dict[str, Game] = {}
        self.correspondence: dict[str, Game] = {}

    def _get_speed_dict(self, speed: str) -> dict[str, Game]:
        if speed not in {"bullet", "blitz", "rapid", "classical", "correspondence"}:
            raise ValueError(f"Unknown speed: {speed}")
        return getattr(self, speed)

    def add_game(self, game: Game):
        """Add a single Game to the appropriate category based on speed."""
        speed_dict = self._get_speed_dict(game.speed)
        speed_dict[game.id] = game

    def add_games(self, games: list[Game]):
        """Add multiple games at once."""
        for game in games:
            self.add_game(game)

    def get_game_on_id(self, game_id: str) -> Game:
        """Searches all categories for a game with the given ID."""
        for speed in ["ultraBullet", "bullet", "blitz", "rapid", "classical", "correspondence"]:
            speed_dict = getattr(self, speed)
            if game_id in speed_dict:
                return speed_dict[game_id]
        raise KeyError(f"Game ID '{game_id}' not found")

    def get_games_on_speed(self, speed: str) -> list[Game]:
        """Returns a list of games for a given speed."""
        return list(self._get_speed_dict(speed).values())

    def __repr__(self) -> str:
        return (f"Player(username={self.username}, "
            f"ultraBullet={len(self.bullet)}, "
            f"bullet={len(self.bullet)}, "
            f"blitz={len(self.blitz)}, "
            f"rapid={len(self.rapid)}, "
            f"classical={len(self.classical)}, "
            f"correspondence={len(self.correspondence)})")

    def get_all_games_df(self) -> pd.DataFrame:
        all_games = []
        for speed in ["ultraBullet", "bullet", "blitz", "rapid", "classical", "correspondence"]:
            speed_dict = getattr(self, speed)
            for game in speed_dict.values():
                all_games.append(game.to_dataframe())
        if all_games:
            return pd.concat(all_games, ignore_index=True)
        return pd.DataFrame()