from socketio import AsyncServer
from controller.music_controller import MusicHandlers


class MusicSocketRouter:
    def __init__(self, sio: AsyncServer):
        self.sio = sio
        self.handler = MusicHandlers(sio)
        self._register_events()

    def _register_events(self):
        self.sio.on("music:play")(self.handler.handle_play)
        self.sio.on("music:pause")(self.handler.handle_pause)
        self.sio.on("music:seek")(self.handler.handle_seek)
        self.sio.on("music:add_to_playlist")(self.handler.handle_add_to_playlist)
        self.sio.on("music:join_room")(self.handler.handle_join_room)
        self.sio.on("music:vote_skip")(self.handler.handle_vote_skip)
