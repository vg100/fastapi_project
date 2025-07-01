from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from model.user_model import UserModel
from bson import ObjectId

# await request.state.redis.set("message", "Hello Redis Cloud!")
# await request.state.sio.emit("user_signup", {"message": "New signup!"})
# request.state.logger.info("jjjj")


class UserController:

    @staticmethod
    async def signup(request: Request):
        db = request.state.db
        body = await request.json()
        # Validate input
        try:
            user = UserModel(**body)
            existing = await db["users"].find_one({"email": user.email})
            if existing:
                raise HTTPException(status_code=400, detail="Email already registered")
            await db["users"].insert_one(user.dict(by_alias=True))
            return JSONResponse(body)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Error: {str(e)}")

    @staticmethod
    async def login(request: Request):
        try:
            db = request.state.db
            body = await request.json()
            user = await db["users"].find_one({"email": body.get("email")})
            if "_id" in user and isinstance(user["_id"], ObjectId):
                user["_id"] = str(user["_id"])
            return JSONResponse(
                status_code=200,
                content={"message": "Login successful", "user": user},
            )
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Error: {str(e)}")
