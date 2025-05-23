import requests
from typing import Optional
from datetime import datetime
from platforms.platform_abc import PlatformWrapper

class LichessWrapper(PlatformWrapper):
    def __init__(self, platform_config: dict[str, any]) -> None:
        self._name = platform_config['name']
        self.api_url = platform_config["url"]
        self.token = platform_config["token"]

    @property
    def name(self) -> str:
        return self._name

    def get_pgns_by_username(
        self,
        username: str,
        start_dt_utc: Optional[datetime] = None,
        end_dt_utc: Optional[datetime] = None,
        number_of_games: Optional[int] = None
    ) -> str:
        if number_of_games is not None and (start_dt_utc is not None or end_dt_utc is not None):
            raise ValueError("Cannot specify number_of_games with start_dt_utc or end_dt_utc")
        
        url = f"https://lichess.org/api/games/user/{username}"
        headers = {
            "Accept": "application/x-ndjson",
            "Authorization": f"Bearer {self.token}"
        }
        params = {}

        if number_of_games is not None:
            params["max"] = number_of_games
        else:
            if start_dt_utc:
                params["since"] = int(start_dt_utc.timestamp() * 1000)
            if end_dt_utc:
                params["until"] = int(end_dt_utc.timestamp() * 1000)

        response = requests.get(url, headers=headers, params=params, stream=True)
        response.raise_for_status()

        pgns = []
        for line in response.iter_lines():
            if line:
                import json
                game_data = json.loads(line.decode("utf-8"))
                pgns.append(game_data.get("moves", ""))

        return pgns

