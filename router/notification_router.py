from socketio import AsyncServer
from controller.user_controller import UserController  # Optional: for user verification


class NotificationSocketRouter:
    def __init__(self, sio: AsyncServer):
        self.sio = sio
        self._events()
        self.connected_users = {}

    def _events(self):
        @self.sio.on("notification:subscribe")
        async def handle_subscribe(sid, data):
            """
            Client sends: { "user_id": "123" }
            """
            user_id = data.get("user_id")
            if user_id:
                self.connected_users[sid] = user_id
                await self.sio.enter_room(sid, room=user_id)
                await self.sio.emit("notification:subscribed", {"status": "ok"}, to=sid)
                print(f"[Notification] {sid} subscribed to {user_id}")
            else:
                await self.sio.emit(
                    "notification:error", {"message": "user_id required"}, to=sid
                )

        @self.sio.on("notification:send")
        async def handle_send_notification(sid, data):
            """
            Server or admin can send: {
                "user_id": "123",
                "message": "Hello, this is your alert"
            }
            """
            user_id = data.get("user_id")
            message = data.get("message")

            if not user_id or not message:
                await self.sio.emit(
                    "notification:error",
                    {"message": "Missing user_id or message"},
                    to=sid,
                )
                return

            await self.sio.emit(
                "notification:receive", {"message": message}, room=user_id
            )
            print(f"[Notification] Sent to {user_id}: {message}")

        @self.sio.on("notification:broadcast")
        async def handle_broadcast(sid, data):
            """
            Broadcast to all connected users
            { "message": "System-wide alert" }
            """
            message = data.get("message")
            if message:
                await self.sio.emit("notification:receive", {"message": message})
                print("[Notification] Broadcast:", message)
            else:
                await self.sio.emit(
                    "notification:error", {"message": "Message required"}, to=sid
                )
