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

    def get_games_by_username(
        self,
        username: str,
        start_dt_utc: Optional[datetime] = None,
        end_dt_utc: Optional[datetime] = None,
        number_of_games: Optional[int] = None
    ) -> Player:
        if number_of_games is not None and (start_dt_utc is not None or end_dt_utc is not None):
            raise ValueError("Cannot specify number_of_games with start_dt_utc or end_dt_utc")

        response = self._fetch_games(username, start_dt_utc, end_dt_utc, number_of_games)
        return self._parse_games(response.iter_lines(), username)

    def _fetch_games(self, username: str, start_dt_utc: Optional[datetime], end_dt_utc: Optional[datetime], number_of_games: Optional[int]):
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
        return response

    def _parse_games(self, lines, username: str) -> Player:
        player = Player(username)
        for line in lines:
            if not line:
                continue
            try:
                game_data = json.loads(line.decode("utf-8"))
                game = self._create_game_from_data(game_data)
                player.add_game(game)
            except Exception as e:
                print(f"Skipping game due to error: {e}")
        return player

    def _create_game_from_data(self, game_data: dict) -> Game:
        move_list = game_data.get("moves", "").split()
        evals = self._extract_evaluations(game_data, len(move_list))
        clocks = game_data.get("clocks", [])

        return Game(
            id=game_data["id"],
            start_dt_utc=datetime.fromtimestamp(game_data["createdAt"] / 1000),
            platform=self.name,
            speed=game_data.get("speed", "unknown"),
            opening=game_data.get("opening", {}).get("name", "Unknown"),
            status=game_data.get("status", "unknown"),
            winner=game_data.get("winner", "draw") if game_data.get("winner") else "draw",
            moves=move_list,
            evaluations=evals,
            time_spent=clocks
        )

    def _extract_evaluations(self, game_data: dict, move_count: int) -> list[str]:
        evals = []
        for step in game_data.get("analysis", []):
            if "eval" in step:
                evals.append(str(step["eval"]))
            elif "mate" in step:
                mate_score = step["mate"]
                if mate_score > 0:
                    evals.append(f"mate in {mate_score}")
                else:
                    evals.append(f"mated in {abs(mate_score)}")
        return evals[:move_count]