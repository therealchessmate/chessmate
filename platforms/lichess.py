import requests
from datetime import datetime
from typing import Optional

from platforms.platform_abc import PlatformWrapper

class LichessWrapper(PlatformWrapper):
    def __init__(self, token: Optional[str] = None):
        """
        :param token: Optional personal API token from lichess.org
        """
        self.base_url = "https://lichess.org/api"
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                "Authorization": f"Bearer {token}"
            })

    def _to_epoch_millis(self, dt: datetime) -> int:
        return int(dt.timestamp() * 1000)

    def get_pgns_by_user(self, username: str, start_dt: datetime, end_dt: datetime) -> str:
        """
        Fetch PGNs of a Lichess user between two datetimes.

        :param username: Lichess username
        :param start_dt: Start datetime (UTC)
        :param end_dt: End datetime (UTC)
        :return: String of PGNs
        """
        url = f"{self.base_url}/games/user/{username}"

        params = {
            "since": self._to_epoch_millis(start_dt),
            "until": self._to_epoch_millis(end_dt),
            "max": 300,  # max games per request
            "pgnInJson": False,
            "analysed": False,
            "moves": True,
            "clocks": False,
            "evals": False,
            "opening": False
        }

        headers = {
            "Accept": "application/x-chess-pgn"
        }

        response = self.session.get(url, headers=headers, params=params, stream=True)

        if response.status_code != 200:
            raise Exception(f"Lichess API error: {response.status_code} - {response.text}")

        return response.text
