from fastapi import APIRouter, Request, Depends
from controller.user_controller import UserController
from middlewares.auth_dependency import verify_token, rate_limiter
from ai_agents.ascii import AsciiArchitectureAgent


class UserRouter:
    def __init__(self):
        self.router = APIRouter()
        self._postRouter()
        self._getRouter()

    def _getRouter(self):
        self.router.get("/stream")(UserController.stream)
        self.router.get("/ascii")(AsciiArchitectureAgent.generate_diagram)

    def _postRouter(self):
        self.router.post(
            "/signup",
        )(UserController.signup)
        self.router.post("/login")(UserController.login)
        self.router.post("/webhook")(UserController.receive_whatsapp_message)
        self.router.post(
            "/test", dependencies=[Depends(verify_token), Depends(rate_limiter)]
        )(UserController.receive_whatsapp_message)


user_router = UserRouter().router
