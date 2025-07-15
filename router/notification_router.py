from socketio import AsyncServer
from controller.notification import NotificationHandlers


class NotificationSocketRouter:
    def __init__(self, sio: AsyncServer):
        self.sio = sio
        self.handler = NotificationHandlers(sio)
        self._register_events()

    def _register_events(self):
        self.sio.on("notification:subscribe")(self.handler.handle_subscribe)
        self.sio.on("notification:send")(self.handler.handle_send)
        self.sio.on("notification:broadcast")(self.handler.handle_broadcast)
