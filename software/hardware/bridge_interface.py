"""
PC Link - Abstract Bridge Interface
"""
from abc import ABC, abstractmethod
from typing import Callable, Optional, Dict, Any

class BridgeInterface(ABC):
    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass

    @abstractmethod
    def send_packet(self, cmd: int, payload: bytes = b"", flags: int = 0) -> bool:
        pass

    @abstractmethod
    def register_callback(self, callback: Callable[[int, int, bytes], None]) -> None:
        pass

    @abstractmethod
    def get_telemetry(self) -> Dict[str, Any]:
        pass
