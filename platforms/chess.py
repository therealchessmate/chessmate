from typing import Any

from platforms.platform_abc import PlatformWrapper

class ChessWrapper(PlatformWrapper):
    def __init__(self, platform_config: dict[str, Any]) -> None:
        self._name = platform_config['name']
        self.api_url = platform_config["url"]
        self.token = platform_config["token"]

    @property
    def name(self) -> str:
        return self._name