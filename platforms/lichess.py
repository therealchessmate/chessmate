import requests
from typing import Optional
from datetime import datetime
import json
from platforms.platform_abc import PlatformWrapper
from common_objects.player import Player
from common_objects.game import Game

class LichessWrapper(PlatformWrapper):
    def __init__(self, platform_config: dict[str, any]) -> None:
        self._name = platform_config['name']
        self.api_url = platform_config["url"]
        self.token = platform_config["token"]

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
        if number_of_games is not None and (start_dt_utc is not None or end_dt_utc is not None):
            raise ValueError("Cannot specify number_of_games with start_dt_utc or end_dt_utc")

        url = f"https://lichess.org/api/games/user/{username}"
        headers = {
            "Accept": "application/x-ndjson",
            "Authorization": f"Bearer {self.token}"
        }
        params = {
            "analysed": "true",
            "pgnInJson": "false",
            "clocks": "true",
            "opening": "true",
            "evals": "true"
        }

        if number_of_games is not None:
            params["max"] = number_of_games
        else:
            if start_dt_utc:
                params["since"] = int(start_dt_utc.timestamp() * 1000)
            if end_dt_utc:
                params["until"] = int(end_dt_utc.timestamp() * 1000)

        response = requests.get(url, headers=headers, params=params, stream=True)
        response.raise_for_status()

        player = Player(username)
        for line in response.iter_lines():
            if not line:
                continue

            game_data = json.loads(line.decode("utf-8"))

            try:
                move_list = game_data.get("moves", "").split()

                # Get evaluations from analysis
                evals = []
                if "analysis" in game_data:
                    for step in game_data["analysis"]:
                        eval_info = step.get("eval")
                        if eval_info is not None:
                            evals.append(eval_info)
                evals = evals[:len(move_list)]  # ensure same length

                # Get time spent from clock data
                times = []
                if "clock" in game_data and "clock" in game_data["clock"]:
                    times = game_data["clock"]["clock"]
                    if isinstance(times, list):
                        times = times[:len(move_list)]

                game = Game(
                    id=game_data["id"],
                    start_dt_utc=datetime.fromtimestamp(game_data["createdAt"] / 1000),
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
            except Exception as e:
                print(f"Skipping game due to error: {e}")