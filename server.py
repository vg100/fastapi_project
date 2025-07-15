from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from motor.motor_asyncio import AsyncIOMotorClient
from router.user_router import user_router
from router.notification_router import NotificationSocketRouter
import socketio
import redis.asyncio as redis
import logging
from fastapi.staticfiles import StaticFiles
from setting import settings


# ================== SERVER =======================
class Server:
    def __init__(self):
        self.logger = logging.getLogger("uvicorn")
        self.mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
        self.db = self.mongo_client["auttodo"]
        self.sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
        self.fastapi_app = FastAPI(title="Project API", version="1.0.0")
        self.app = socketio.ASGIApp(self.sio, self.fastapi_app)
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self._setup()

    def _setup(self):
        self._setup_events()
        self._setup_middlewares()
        self._setup_routes()
        self._setup_socket_handlers()
        self._setup_error_handlers()
        self._404_error_handlers()

    # ---------- Startup/Shutdown Lifecycle ----------
    def _setup_events(self):
        @self.fastapi_app.on_event("startup")
        async def on_startup():
            await self.mongo_client.admin.command("ping")
            self.logger.info("✅ MongoDB connected successfully")

            await self.redis_client.ping()
            self.logger.info("✅ Redis connected successfully")

        @self.fastapi_app.on_event("shutdown")
        async def on_shutdown():
            await self.redis_client.close()
            await self.mongo_client.close()

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

        @self.fastapi_app.middleware("http")
        async def rate_limiter(request: Request, call_next):
            ip = request.client.host
            key = f"rate-limit:{ip}"
            count = await self.redis_client.get(key)

            if count and int(count) >= 1000:
                raise Exception("Too Many Requests")
            pipeline = self.redis_client.pipeline()
            pipeline.incr(key, 1)
            pipeline.expire(key, 60)
            await pipeline.execute()
            return await call_next(request)

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
        NotificationSocketRouter(self.sio)

        @self.sio.event
        async def connect(sid, environ):
            print(f"🟢 Socket connected: {sid}")
            await self.sio.emit("welcome", {"message": "Welcome!"}, to=sid)

        @self.sio.event
        async def disconnect(sid):
            print(f"🔴 Socket disconnected: {sid}")

    # --------------- Error Handling -----------------
    def _setup_error_handlers(self):
        @self.fastapi_app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            response_data = {"status": "error", "path": request.url.path}
            # if isinstance(exc, HTTPException):
            #     response_data["message"] = exc.detail
            #     return JSONResponse(status_code=exc.status_code, content=response_data)

            # elif isinstance(exc, RequestValidationError):
            #     response_data["message"] = "Validation error"
            #     response_data["details"] = exc.errors()
            #     return JSONResponse(status_code=422, content=response_data)

            response_data["message"] = str(exc)
            return JSONResponse(status_code=500, content=response_data)

    def _404_error_handlers(self):
        @self.fastapi_app.middleware("http")
        async def global_error_handler(request: Request, call_next):
            response = await call_next(request)
            if response.status_code == 404:
                return JSONResponse(
                    {"message": "Route not found", "status_code": 404},
                    status_code=404,
                )
            return response
