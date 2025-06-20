from flask import request
from game_errors import *

class Session:
    def __init__(self, data, socketio):
        self.session_id = data["session_id"]
        self.sid = None
        self.player = None
        self.socketio = socketio

    def set_player(self, player):
        self.player = player

    def get_player(self):
        if not self.player: raise SelectionError("Session Has No Associated Player")
        return self.player

    def get_id(self):
        return self.session_id

    def emit(self, method_name, data = None):
        if self.sid is None:
            print("WARNING: self.sid is None")
            return
        if data:
            self.socketio.emit(method_name, data, to=self.sid)
        else:
            self.socketio.emit(method_name, to=self.sid)

    # NOTE: Only works when called from socketio.on
    def update(self, data):
        try:
            self.sid = request.sid
        except:
            raise ValueError("Session.update must be called from a socketio context")

    def is_active(self, sid):
        return sid == self.sid

    def disconnect(self, message = "Session Was Disconnected Intentionally"):
        self.emit("force_disconnect", {"message": message})
        self.sid = None
        self.session_id = None



