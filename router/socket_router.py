from socketio import AsyncServer


def setup_socket_listeners(sio: AsyncServer):

    @sio.event
    async def ping(sid, data):
        print(f"📡 Ping from {sid}: {data}")
        # await sio.emit("pong", {"message": data}, to=sid)
