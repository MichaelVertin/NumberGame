from game_errors import *

class Player:
    def __init__(self, player_name):
        self.name = player_name
        self.session = None
        self.game_room = None

    def get_session(self):
        if not self.session: raise PlayerHasNoSessionError()
        return self.session

    def set_session(self, session):
        print(f"Setting Session for {self.name}")
        self.session = session

    def get_game_room(self):
        if not self.game_room: raise GameDoesNotExistError("Not In A Game")
        return self.game_room

    def join_game_room(self, game_room):
        self.game_room = game_room
        self.game_room.add_player(self)
        self.get_session().emit("load_game")

    def set_state(self, state = None):
        if not state: state = self.get_game_room().get_state()
        session = self.get_session()
        session.emit("set_state", state)

    def do_turn(self, data):
        game_room = self.get_game_room()
        session = self.get_session()
        try:
            game_room.do_turn(self, data)
            session.emit("set_selection_status", {"status": "True", "message": "Turn Completed Successfully"})
        except InvalidMoveError as e:
            session.emit("set_selection_status", {"status": "False", "message": str(e)})

    def validate_turn(self, data):
        game_room = self.get_game_room()
        session = self.get_session()
        # TODO: Should this be in the main program? 
        try:
            status = game_room.validate_turn(self, data)
            session.emit("set_selection_status", status)

        except InvalidMoveError as e:
            session.emit("set_selection_status", {"status": "False", "message":str(e)})

    def on_load_game(self):
        game_room = self.get_game_room()
        players = game_room.get_players()

        your_name = self.name
        if your_name not in players:
            your_name = players[0]

        data = {"your_name": your_name, 
                "opponent_name": [name for name in players if name != your_name][0]
               }
        self.get_session().emit("set_names", data)

    def emit(self, method_name, data = None):
        session = self.get_session()
        session.emit(method_name, data)

    def abandon_session(self):
        print(f"Abandoning Session {self.session} for {self.name}")
        prev_session = self.session
        self.session = None
        return prev_session




