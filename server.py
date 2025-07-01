from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from motor.motor_asyncio import AsyncIOMotorClient
from router.user_router import user_router
from router.socket_router import setup_socket_listeners
import socketio
import redis.asyncio as redis
import logging
from fastapi.staticfiles import StaticFiles


# ================== SERVER =======================
class Server:
    def __init__(self):
        self.logger = logging.getLogger("uvicorn")
        self.mongo_client = AsyncIOMotorClient(
            "mongodb+srv://vg100:vg100@cluster0.bszog.mongodb.net/auttodo?retryWrites=true&w=majority"
        )
        self.db = self.mongo_client["auttodo"]
        self.sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
        self.fastapi_app = FastAPI(title="Project API", version="1.0.0")
        self.app = socketio.ASGIApp(self.sio, self.fastapi_app)
        self.redis_client = redis.from_url(
            "redis://default:WD0FlpOtf3IE7OKRxcGCLOCQ1bit07WD@redis-11167.crce182.ap-south-1-1.ec2.redns.redis-cloud.com:11167",
            decode_responses=True,
        )
        self._setup()

    def _setup(self):
        self._setup_events()
        self._setup_middlewares()
        self._setup_routes()
        self._setup_socket_handlers()
        self._setup_error_handlers()

    # ---------- Startup/Shutdown Lifecycle ----------
    def _setup_events(self):
        @self.fastapi_app.on_event("startup")
        async def on_startup():
            print("🚀 FastAPI starting up...")

        @self.fastapi_app.on_event("shutdown")
        async def on_shutdown():
            print("🛑 FastAPI shutting down...")
            await self.redis_client.close()

    # --------------- Middlewares --------------------
    def _setup_middlewares(self):
        self.fastapi_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.fastapi_app.middleware("http")
        async def attach_dependencies(request: Request, call_next):
            request.state.sio = self.sio
            request.state.redis = self.redis_client
            request.state.logger = self.logger
            request.state.db = self.db
            return await call_next(request)

        @self.fastapi_app.middleware("http")
        async def log_requests(request: Request, call_next):
            self.logger.info(f"[{request.method}] {request.url}")
            response = await call_next(request)
            self.logger.info(f"[{response.status_code}] {request.url}")
            return response

    # --------------- Routes -------------------------
    def _setup_routes(self):
        @self.fastapi_app.get("/", tags=["Health"])
        def health_check():
            return {"name": "Test", "status": "UP"}

        self.fastapi_app.mount(
            "/uploads", StaticFiles(directory="uploads"), name="upload"
        )
        self.fastapi_app.include_router(user_router, prefix="/auth", tags=["Auth"])

    # --------------- Socket.IO Handlers -------------
    def _setup_socket_handlers(self):
        setup_socket_listeners(self.sio)

        @self.sio.event
        async def connect(sid, environ):
            print(f"🟢 Socket connected: {sid}")
            await self.sio.emit("welcome", {"message": "Welcome!"}, to=sid)

        @self.sio.event
        async def disconnect(sid):
            print(f"🔴 Socket disconnected: {sid}")

    # --------------- Error Handling -----------------
    def _setup_error_handlers(self):
        @self.fastapi_app.middleware("http")
        async def global_error_handler(request: Request, call_next):
            try:
                response = await call_next(request)
                if response.status_code == 404:
                    return JSONResponse(
                        {"message": "Route not found", "status_code": 404},
                        status_code=404,
                    )
                return response
            except Exception as e:
                return await self._handle_exception(request, e)

    async def _handle_exception(self, request: Request, error: Exception):
        print(f"❌ Exception: {error}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error", "detail": str(error)},
        )
