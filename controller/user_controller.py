from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from model.user_model import UserModel
from bson import ObjectId
from ai_agents.gemini_agent import gemini_agent
from utils.utils import create_access_token
import httpx

# await request.state.redis.set("message", "Hello Redis Cloud!")
# await request.state.sio.emit("user_signup", {"message": "New signup!"})
# request.state.logger.info("jjjj")


class UserController:

    @staticmethod
    async def signup(request: Request):
        db = request.state.db
        body = await request.json()
        # Validate input
        user = UserModel(**body)
        existing = await db["users"].find_one({"email": user.email})
        if existing:
            raise Exception("Email already registered")
        await db["users"].insert_one(user.dict(by_alias=True))
        return JSONResponse(body)

    @staticmethod
    async def login(request: Request):
        db = request.state.db
        body = await request.json()
        user = await db["users"].find_one({"email": body.get("email")})
        if not user:
            raise Exception("User not found")

        if "_id" in user and isinstance(user["_id"], ObjectId):
            user["_id"] = str(user["_id"])
            token = create_access_token({"sub": user["_id"], "email": user["email"]})
        return JSONResponse(
            status_code=200,
            content={"message": "Login successful", "user": user, "token": token},
        )

    @staticmethod
    async def get_profile(request: Request):
        db = request.state.db
        user = await db["users"].find_one({"email": request.state.user["email"]})
        if not user:
            raise Exception("User not found")

        if "_id" in user and isinstance(user["_id"], ObjectId):
            user["_id"] = str(user["_id"])
        return JSONResponse(
            status_code=200,
            content={"user": user},
        )

    @staticmethod
    async def stream(request: Request):
        prompt = request.query_params.get("prompt")
        if not prompt:
            return StreamingResponse(
                iter(["Missing 'prompt' query parameter"]), media_type="text/plain"
            )

        async def generator():
            # calling async method that yields normally
            async for chunk in gemini_agent.stream(prompt):
                yield chunk

        return StreamingResponse(generator(), media_type="text/plain")

    @staticmethod
    async def receive_whatsapp_message(request: Request):
        BLOCKED_NUMBERS = ["919876543210", "911234567890"]
        chat_id = body["data"].get("chatId", "")
        body = await request.json()
        sender = body["data"].get("from")
        message = body["data"].get("body")
        print(message, sender)

        # Skip blocked numbers
        if sender in BLOCKED_NUMBERS:
            print(f"Blocked user: {sender}")
            return {"status": "ignored"}

        # Skip group chats
        if "@g.us" in chat_id:
            print("Group message skipped")
            return {"status": "group_skipped"}

        if sender and message:
            reply = gemini_agent.ask(message)

            # Send reply back to WhatsApp user
            async with httpx.AsyncClient() as client:
                await client.post(
                    "https://api.ultramsg.com/instance129831/messages/chat",
                    params={"token": "lu09e8bsqanwvexc"},
                    json={"to": sender, "body": reply},
                )
        return {"status": "ok"}
