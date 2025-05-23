import requests
from datetime import datetime
from typing import Optional

from platforms.platform_abc import PlatformWrapper

class ChessWrapper(PlatformWrapper):
    def __init__(self, token: Optional[str] = None):
        pass