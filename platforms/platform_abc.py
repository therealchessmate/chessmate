from abc import ABC, abstractmethod

class PlatformWrapper(ABC):
    @abstractmethod
    def run(self) -> None:
        """Start the platform's main process."""
        pass

