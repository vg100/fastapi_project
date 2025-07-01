from fastapi import APIRouter, Request, Depends
from controller.user_controller import UserController
from middlewares.auth_dependency import verify_token


class UserRouter:
    def __init__(self):
        self.router = APIRouter()
        self._postRouter()

    def _postRouter(self):
        self.router.post("/signup", dependencies=[Depends(verify_token)])(
            UserController.signup
        )
        self.router.post("/login")(UserController.login)


user_router = UserRouter().router
