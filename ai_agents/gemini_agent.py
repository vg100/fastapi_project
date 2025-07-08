import google.generativeai as genai
from .base import AIAgent


class GeminiAgent(AIAgent):
    def __init__(self, api_key: str = "AIzaSyCDzCzWNrMwfQBThHlu1sNs3_wF2fcYZxc"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def generate(self, prompt: str) -> str:
        response = await self.model.generate_content_async(prompt)
        return response.text.strip()

    async def stream(self, prompt: str):
        stream = self.model.generate_content(prompt, stream=True)
        async for chunk in stream:
            yield chunk.text

    async def metadata(self):
        return {"model": "Gemini-Pro", "provider": "Google", "supports_streaming": True}

    def ask(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error: {str(e)}"


gemini_agent = GeminiAgent()
