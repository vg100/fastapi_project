import openai
from .base import AIAgent


class OpenAIAgent(AIAgent):
    def __init__(self, api_key: str):
        openai.api_key = api_key

    async def generate(self, prompt: str) -> str:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()


openai_agent = OpenAIAgent()
