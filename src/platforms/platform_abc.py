from abc import ABC, abstractmethod
from datetime import datetime
from common_objects.player import Player

class PlatformWrapper(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the platform, e.g., 'lichess'."""
        pass

from typing import Optional

class PlatformWrapper(ABC):

    @abstractmethod
    def get_games_by_username(
        self,
        username: str,
        start_dt_utc: Optional[datetime] = None,
        end_dt_utc: Optional[datetime] = None,
        number_of_games: Optional[int] = None
    ) -> Player:
        """
        Fetch PGNs for a user.

        Rules:
        - If `number_of_games` is specified, `start_dt_utc` and `end_dt_utc` must NOT be specified.
        - If `number_of_games` is None, `start_dt_utc` and `end_dt_utc` can be used to specify a date range.
        - If none of the optional params are specified, fetch all or use some default range.
        """
        pass