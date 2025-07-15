class NotificationHandlers:
    def __init__(self, sio):
        self.sio = sio
        self.connected_users = {}  # Maintain room mapping here

    async def handle_subscribe(self, sid, data):
        """
        Client sends: { "user_id": "123" }
        """
        user_id = data.get("user_id")
        if user_id:
            self.connected_users[sid] = user_id
            await self.sio.enter_room(sid, room=user_id)
            await self.sio.emit("notification:subscribed", {"status": "ok"}, to=sid)
            print(f"[Notification] {sid} subscribed to room {user_id}")
        else:
            await self.sio.emit(
                "notification:error", {"message": "user_id required"}, to=sid
            )

    async def handle_send(self, sid, data):
        """
        Client sends: { "user_id": "123", "message": "..." }
        """
        user_id = data.get("user_id")
        message = data.get("message")

        if not user_id or not message:
            await self.sio.emit(
                "notification:error", {"message": "Missing user_id or message"}, to=sid
            )
            return

        await self.sio.emit("notification:receive", {"message": message}, room=user_id)
        print(f"[Notification] Sent to user {user_id}: {message}")

    async def handle_broadcast(self, sid, data):
        """
        Client sends: { "message": "..." }
        """
        message = data.get("message")
        if message:
            await self.sio.emit("notification:receive", {"message": message})
            print(f"[Notification] Broadcast: {message}")
        else:
            await self.sio.emit(
                "notification:error", {"message": "Message required"}, to=sid
            )
