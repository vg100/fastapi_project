from ai_agents.gemini_agent import GeminiAgent
from ai_agents.base import AIAgent


class TranslatorAgent(AIAgent):
    def __init__(self):
        self.agent = GeminiAgent()
        self.lang = "En"

    async def generate(self, prompt: str) -> str:
        return await self.agent.generate(f"Translate to {self.lang}: {prompt}")
