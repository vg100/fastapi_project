from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional, Dict, Any


class AIAgent(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass

    @abstractmethod
    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        pass
