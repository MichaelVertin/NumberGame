from game_logic import NumberGame


GAME_ROOMS = dict()

class Player:
    def __init__(self, sid, name):
        self.__sid = sid
        self.name = name
        self.game_room = None

    def create_game(self, opponent_name, game_name):
        game = NumberGame(self.name, opponent_name)
        room = GameRoom(game)
        GAME_ROOMS[game_name] = room

    def join_game(self, game_name):
        game_room = GAME_ROOMS[game_name]
        self.game_room = game_room
        self.game_room.update_state()

    def update_state(self, state):
        emit('set_state', state, to=self.sid)

    def submit_turn(self, turn):
        self.game_room.do_turn(self, turn)

    def validate_turn(self, data):
        self.game_room.check_turn(self, turn)

    def leave_room(self):
        if self.game_room:
            self.game_room.remove_player(self)
            self.game_room = None

class GameRoom:
    def __init__(self, game):
        self.players = dict()
        self.game = game
        
    def add_player(self, player):
        self.players[player.name] = player

    def remove_player(self, player):
        del self.players[player.name]

    def update_state(self):
        state = self.game.get_state()
        active_player = self.game.get_active_player()
        score = self.game.get_score()

        state = {"cards": state, 
                 "active_player": active_player, 
                 "score": score}
        for player in self.players.items():
            player.update_state(state)

    def submit_turn(self, player, data):
        if player.name != self.game.get_active_player():
            raise SelectionError("Not Your Turn")
        self.turn.validate()
        self.update_state()

    def validate_turn(self, player, data):
        if player.name != self.game.get_active_player():
            raise SelectionError("Not Your Turn")
        self.turn.execute()

