from logging import getLogger
from typing import Self

from data.helper_functions import load_class
from platforms.platform_abc import PlatformWrapper



from typing import Self

class DispatcherApp:
    def __init__(self, platforms: list[PlatformWrapper]):
        self.platforms = platforms

    @classmethod
    def run(cls, config: dict) -> Self:
        platforms_config = config.get("platforms", [])
        platforms = []

        for platform_cfg in platforms_config:
            if not platform_cfg.get("enabled", False):
                continue

            class_path = platform_cfg["class"]
            wrapper_cls = load_class(class_path)
            platforms.append(wrapper_cls(platform_cfg))  # Pass full config

        return cls(platforms)
       

    # def analyse(self,
    #         name,
    #         start_dt_utc:datetime,
    #         end_dt_utc: datetime):
    #     evaluated_pgns = {}

    #     #
    #     pgns = lichess_wrapper.get_pgns_by_user(name,start_dt_utc, end_dt_utc)
    #     for pgn in pgns:
    #         evaluated_pgn = stockfish_wrapper.evaluate_game(pgn)
    #         evaluated_pgns[evaluated_pgn.id] = evaluated_pgn
    #     clusters = cluster_analysis(evaluated_pgns)
    #     mistakes = mistake_identifier(clusters)
    #     biggest_impact_mistakes = ImpactFinder(mistakes)


        



        

        
        
