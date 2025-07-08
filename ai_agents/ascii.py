from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from ai_agents.gemini_agent import gemini_agent
import re

SYSTEM_CONTEXT = """
You are a system architect assistant. When given a keyword or short phrase (e.g., "ecommerce", "chatbot", "banking system"),
you must first imagine and expand it into a detailed high-level software architecture. 
Include the major components, services, data stores, and APIs typically involved.

Then, generate an **ASCII-style diagram** representing the architecture. 
Only return the diagram — no explanation, no markdown formatting, and no code block.
"""


class AsciiArchitectureAgent:
    @staticmethod
    async def generate_diagram(request: Request):
        keyword = request.query_params.get("prompt")
        if not keyword:
            raise HTTPException(
                status_code=400, detail="Missing 'prompt' query parameter."
            )

        full_prompt = f"""{SYSTEM_CONTEXT}

Generate an ASCII architecture diagram for: {keyword}
"""

        try:
            response = await gemini_agent.generate(full_prompt)
            print(response)
            return JSONResponse(content={"diagram": response})
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error generating diagram: {str(e)}"
            )
