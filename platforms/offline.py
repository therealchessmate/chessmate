import json
from typing import Any, Optional
from datetime import datetime
from pathlib import Path

from platforms.platform_abc import PlatformWrapper
from common_objects.player import Player
from common_objects.game import Game

class OfflineWrapper(PlatformWrapper):
    def __init__(self, platform_config: dict[str, Any]) -> None:
        self._name = platform_config['name']
        self.data_path = Path(platform_config['path'])  # path to the NDJSON file or JSON list

    @property
    def name(self) -> str:
        return self._name

    def get_player_by_username(
        self,
        username: str,
        start_dt_utc: Optional[datetime] = None,
        end_dt_utc: Optional[datetime] = None,
        number_of_games: Optional[int] = None
    ) -> Player:
        player = Player(username)
        games_loaded = 0

        with self.data_path.open('r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue

                try:
                    game_data = json.loads(line)

                    created_at = datetime.fromtimestamp(game_data["createdAt"] / 1000)
                    if start_dt_utc and created_at < start_dt_utc:
                        continue
                    if end_dt_utc and created_at > end_dt_utc:
                        continue

                    move_list = game_data.get("moves", "").split()

                    evals = []
                    if "analysis" in game_data:
                        for step in game_data["analysis"]:
                            eval_info = step.get("eval")
                            if eval_info is not None:
                                evals.append(eval_info)
                    evals = evals[:len(move_list)]

                    times = []
                    if "clock" in game_data and "clock" in game_data["clock"]:
                        times = game_data["clock"]["clock"]
                        if isinstance(times, list):
                            times = times[:len(move_list)]

                    game = Game(
                        id=game_data["id"],
                        start_dt_utc=created_at,
                        platform=self.name,
                        speed=game_data.get("speed", "unknown"),
                        opening=game_data.get("opening", {}).get("name", "Unknown"),
                        status=game_data.get("status", "unknown"),
                        winner=game_data.get("winner", "draw") if game_data.get("winner") else "draw",
                        moves=move_list,
                        evaluations=evals,
                        time_spent=times
                    )

                    player.add_game(game)
                    games_loaded += 1
                    print(game.to_dataframe())

                    if number_of_games is not None and games_loaded >= number_of_games:
                        break

                except Exception as e:
                    print(f"Skipping game due to error: {e}")

        return player
