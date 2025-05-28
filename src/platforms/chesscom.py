import requests
import re

from typing import Optional
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from platforms.platform_abc import PlatformWrapper
from common.player import Player
from common.game import Game


class ChessComWrapper(PlatformWrapper):
    def __init__(self, platform_config: dict[str, any]) -> None:
        self._name = platform_config['name']
        self.api_url = platform_config["url"]

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
        if start_dt_utc is None:
            start_dt_utc = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if end_dt_utc is None:
            end_dt_utc = datetime.now(timezone.utc)

        start_dt_utc = start_dt_utc.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_dt_utc = (end_dt_utc.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + relativedelta(months=1))

        player = Player(username)
        collected_games = 0
        current_month = end_dt_utc - relativedelta(months=1)

        while current_month >= start_dt_utc:
            games = self._fetch_games_for_month(username, current_month.year, current_month.month)
            self._parse_games(games, player, number_of_games, collected_games)
            if number_of_games and collected_games >= number_of_games:
                break
            current_month -= relativedelta(months=1)

        return player

    def _fetch_games_for_month(self, username: str, year: int, month: int) -> list[dict]:
        url = f"{self.api_url}/player/{username}/games/{year}/{month:02d}"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; ChessComWrapper/1.0; +https://github.com/therealchessmate/chessmate)"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("games", [])

    def _parse_games(self, games: list[dict], player: Player, max_games: Optional[int], collected_games: int):
        for game_data in games:
            if game_data.get("rules") != "chess":
                continue  # Skip chess960, atomic, etc.

            try:
                game = self._create_game_from_data(game_data, player.username)
                player.add_game(game)
                collected_games += 1
                if max_games and collected_games >= max_games:
                    break
            except Exception as e:
                print(f"Skipping game due to error: {e}")
                


    def _create_game_from_data(self, game_data: dict, username: str) -> Game:
        pgn = game_data.get("pgn", "")

        try:
            moves_section = pgn.split("\n\n", 1)[1].replace("\n", " ")
        except IndexError:
            raise ValueError("Invalid PGN format")

        # Match lines like:
        # 1. e4 {[%clk 0:10:00]}
        # 1... e6 {[%clk 0:09:55]}
        move_pattern = re.compile(
            r'(?P<number>\d+)\.(?P<dots>\.\.)?\s*(?P<move>\S+)(?:\s*\{\[%clk (?P<clk>[^\]]+)\]\})?'
        )

        def parse_clock(clk: str | None) -> float | None:
            if not clk:
                return None
            parts = clk.split(":")
            if len(parts) == 3:
                h, m, s = int(parts[0]), int(parts[1]), float(parts[2])
            elif len(parts) == 2:
                h, m, s = 0, int(parts[0]), float(parts[1])
            else:
                return None
            return h * 3600 + m * 60 + s

        moves = []
        time_spent = []

        prev_white_clock = None
        prev_black_clock = None

        for match in move_pattern.finditer(moves_section):
            is_black = match.group("dots") == ".."
            move = match.group("move")
            clock_str = match.group("clk")
            clock = parse_clock(clock_str)

            moves.append(move)

            if is_black:
                if clock is not None and prev_black_clock is not None:
                    time_spent.append(prev_black_clock - clock)
                else:
                    time_spent.append(None)
                if clock is not None:
                    prev_black_clock = clock
            else:
                if clock is not None and prev_white_clock is not None:
                    time_spent.append(prev_white_clock - clock)
                else:
                    time_spent.append(None)
                if clock is not None:
                    prev_white_clock = clock

        # Metadata
        start_dt_utc = datetime.fromtimestamp(game_data.get("end_time", 0), tz=timezone.utc)

        white = game_data.get("white", {})
        black = game_data.get("black", {})
        if white.get("result") == "win":
            winner = "white"
        elif black.get("result") == "win":
            winner = "black"
        elif white.get("result") == "stalemate" or black.get("result") == "stalemate":
            winner = "draw"
        elif game_data.get("result") == "1/2-1/2":
            winner = "draw"
        else:
            winner = "unknown"

        if white.get("username", "").lower() == username.lower():
            player_color = "white"
        elif black.get("username", "").lower() == username.lower():
            player_color = "black"
        else:
            raise ValueError("Username not found in white or black fields")

        opening = (game_data.get("eco", "") + " " + game_data.get("opening", "")).strip() or "Unknown"

        return Game(
            id=game_data.get("url", ""),
            start_dt_utc=start_dt_utc,
            platform=self.name,
            speed=game_data.get("time_class", "unknown"),
            opening=opening,
            winner=winner,
            moves=moves,
            evaluations=[],
            time_spent=time_spent,
            player_color=player_color
        )
