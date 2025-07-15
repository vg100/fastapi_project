class MusicHandlers:
    def __init__(self, sio):
        self.sio = sio

    async def handle_play(self, sid, data):
        print(f"[{sid}] ▶️ Playing: {data}")
        await self.sio.emit("music:play", data, room=data["roomId"])

    async def handle_pause(self, sid, data):
        print(f"[{sid}] ⏸️ Paused")
        await self.sio.emit("music:pause", data, room=data["roomId"])

    async def handle_seek(self, sid, data):
        print(f"[{sid}] ⏩ Seeked to: {data['timestamp']}s")
        await self.sio.emit("music:seek", data, room=data["roomId"])

    async def handle_add_to_playlist(self, sid, data):
        print(f"[{sid}] ➕ Added song to playlist: {data['song']}")
        await self.sio.emit("music:playlist_updated", data, room=data["roomId"])

    async def handle_join_room(self, sid, data):
        print(f"[{sid}] 👤 Joined room: {data['roomId']}")
        await self.sio.enter_room(sid, data["roomId"])
        await self.sio.emit(
            "music:user_joined", {"user": data["user"]}, room=data["roomId"]
        )

    async def handle_vote_skip(self, sid, data):
        print(f"[{sid}] 🗳️ Voted to skip")
        await self.sio.emit("music:vote_skip", data, room=data["roomId"])
