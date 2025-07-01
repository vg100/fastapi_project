from fastapi import Request
from fastapi.responses import JSONResponse


class UserController:
    @staticmethod
    async def signup(request: Request):
        await request.state.redis.set("message", "Hello Redis Cloud!")
        await request.state.sio.emit("user_signup", {"message": "New signup!"})
        request.state.logger.info("jjjj")
        return JSONResponse({"message": "User signed up"})

    @staticmethod
    def login(request: Request):
        return JSONResponse({"message": "User logged in"})
