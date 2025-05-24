from datetime import datetime
from typing import Self, Optional

from data.helper_functions import load_class
from platforms.platform_abc import PlatformWrapper

class DispatcherApp:
    def __init__(self, platforms: list[PlatformWrapper]):
        self.platforms = platforms

    @classmethod
    def start(cls, config: dict) -> Self:
        platforms_config = config.get("platforms", [])
        platforms = []

        for platform_cfg in platforms_config:
            if not platform_cfg.get("enabled", False):
                continue

            class_path = platform_cfg["class"]
            wrapper_cls = load_class(class_path)
            platforms.append(wrapper_cls(platform_cfg))  # Pass full config
        dispatcher_app = cls(platforms)
        return dispatcher_app
       
    def analyse(self,
            username: str,
            platform_name: str,
            start_dt_utc: Optional[datetime] = None,
            end_dt_utc: Optional[datetime] = None,
            number_of_games: Optional[int] = None
            ):
        evaluated_pgns = {}

        platform_wrapper = self._find_platform_wrapper(platform_name)
        player = platform_wrapper.get_player_by_username(username, start_dt_utc, end_dt_utc, number_of_games)
        print(player)
    #     for pgn in pgns:
    #         evaluated_pgn = stockfish_wrapper.evaluate_game(pgn)
    #         evaluated_pgns[evaluated_pgn.id] = evaluated_pgn
    #     clusters = cluster_analysis(evaluated_pgns)
    #     mistakes = mistake_identifier(clusters)
    #     biggest_impact_mistakes = ImpactFinder(mistakes)

    def _find_platform_wrapper(self,
                      platform_name: str) -> PlatformWrapper:
        platform_wrapper = next(
            (p for p in self.platforms if p.name == platform_name),
            None
            )

        if platform_wrapper is None:
            raise ValueError(f"No platform wrapper found for platform '{platform_name}'")
        
        return platform_wrapper
        


        



        

        
        
