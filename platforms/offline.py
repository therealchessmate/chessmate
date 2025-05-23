from typing import Any

from platforms.platform_abc import PlatformWrapper

class OfflineWrapper(PlatformWrapper):
    def __init__(self, platform_config: dict[str, Any]) -> None:
        self._name = platform_config['name']

    @property
    def name(self) -> str:
        return self._name