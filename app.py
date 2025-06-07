import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from game_logic import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret'
socketio = SocketIO(app, async_mode='eventlet')

def get_turn_obj(data, game):
    if data["type"] == "draw":
        turn_obj = Turn_Draw(game)
    elif data["type"] == "attack":
        turn_obj = Turn_Attack(game, 
                              data["cards"])
    else:
        raise SelectionError("To draw, only select the deck") # TODO # implement this into javascript
    return turn_obj

class Session:
    def __init__(self, data):
        self.session_id = data["session_id"]
        self.sid = None
        self.player = None
        self.update(data)

    def set_player(self, player):
        self.player = player

    def get_player(self):
        if not self.player: raise SelectionError("Session Has No Associated Player")
        return self.player

    def emit(self, method_name, data = None):
        if data != None:
            socketio.emit(method_name, data, to=self.sid)
        else:
            socketio.emit(method_name, to=self.sid)

    # NOTE: Only works when called from socketio.on
    def update(self, data):
        try:
            self.sid = request.sid
        except:
            self.sid = None

    def disconnect(self):
        print(f"Disconnecting {self.sid}")
        self.emit("force_disconnect")
        self.sid = None
        self.session_id = None


class Player:
    def __init__(self, player_name):
        self.name = player_name
        self.session = None
        self.game_room = None

    def get_session(self):
        if not self.session: raise SelectionError("Session Not Initialized")
        return self.session

    def get_game_room(self):
        if not self.game_room: raise SelectionError("Not In A Game")
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
        except SelectionError as e:
            session.emit("set_selection_status", {"status": "False", "message": str(e)})

    def validate_turn(self, data):
        game_room = self.get_game_room()
        session = self.get_session()
        try:
            status = game_room.validate_turn(self, data)
            session.emit("set_selection_status", status)

        except SelectionError as e:
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

class Lobby:
    def __init__(self):
        self.__players = list()

    def add_player(self, player):
        self.__players.append(player)
    
    def remove_player(self, player):
        # TODO: Error: This is called when player is not in lobby
        self.__players.remove(player)

    def get_player_data(self):
        return PLAYERS

    def get_game_data(self):
        game_data = dict()
        for game_name, game_room in GAME_ROOMS.items():
            player_names = game_room.get_players()
            game_data[game_name] = {
                    "player1": player_names[0], 
                    "player2": player_names[1]
            }
        return game_data

    def get_player_data(self):
        player_data = dict()
        for player_name, player in PLAYERS.items():
            player_data[player_name] = {}

        return player_data

    def set_game_data(self, player = None):
        if player:
            players = [player]
        else:
            players = self.__players

        game_data = self.get_game_data()
        for player in players:
            player.emit("set_games", game_data)

    def set_player_data(self, player = None):
        if player:
            players = [player]
        else:
            players = self.__players

        player_data = self.get_player_data()
        for player in players:
            player.emit("set_players", player_data)





class GameRoom:
    def __init__(self, game, name):
        self.__game = game
        self.__room_id = name
        self.__players = list()
        
    def validate_turn(self, player, data):
        if self.__game.get_active_player() != player.name:
            raise SelectionError("Not Your Turn")
        turn_obj = get_turn_obj(data, self.__game)
        status = turn_obj.validate()
        return status

    def do_turn(self, player, data):
        if self.__game.get_active_player() != player.name:
            raise SelectionError("Not Your Turn")
        turn_obj = get_turn_obj(data, self.__game)
        status = turn_obj.execute()
        self.update_players()

    def add_player(self, player):
        self.__players.append(player)

    def remove_player(self, player):
        self.__players.remove(player)

    def update_players(self):
        game = self.__game
        state = game.get_state()
        for player in self.__players:
            player.set_state(state)

    def get_players(self):
        game = self.__game
        return [game.get_active_player(), game.get_inactive_player()]

    def get_state(self):
        game = self.__game
        state = game.get_state()
        return state


# lobby
LOBBY = Lobby()

# session access
SESSIONS = dict()
def create_session(data):
    session_id = data["session_id"]
    print(f"creating session: {session_id}")
    session = Session(data)
    SESSIONS[session_id] = session
    return session

def get_session(data):
    session_id = data["session_id"]
    # print(f"accessing session: {session_id}")
    if session_id not in SESSIONS:
        return create_session(data)
    return SESSIONS[session_id]

def connect(data):
    try:
        player = get_player(data)
    except SelectionError:
        create_session(data)
        return

    session_id = data["session_id"]
    print(f"connecting session: {session_id}")

    # check player has session
    if player and player.session:
        player_session = player.session
        # if session_id matches, update the session
        if player_session.session_id == session_id:
            player.session.update(data)
        # if session_id does not match, disconnect, and create a new connection
        else:
            player.session.disconnect()
            player.session = None
            del SESSIONS[session_id]
            player.session = create_session(data)
    # if player does not have a session, create the session
    else:
        player.session = create_session(data)
        
    player.session.set_player(player)

def discconnect(data):
    session_id = data["session_id"]
    print(f"disconnecting session: {session_id}")
    session = SESSIONS[session_id]
    if not session: return
    if session.player: session.player.disconnect()
    session.disconnect()
    del SESSIONS[session_id]

# player access
PLAYERS = dict()
def create_player(data):
    player_name = data["username"]
    if player_name in PLAYERS:
        raise SelectionError("Player Already Exists")
    PLAYERS[player_name] = Player(player_name)
    LOBBY.add_player(PLAYERS[player_name])
    LOBBY.set_player_data()

def get_player(data):
    session = get_session(data)
    return session.get_player()

# TODO: Remove unnecessary connects
def set_player(data):
    session = get_session(data)
    player_name = data["username"]
    player = PLAYERS[player_name]
    
    session.set_player(player)
    connect(data)

# game access
GAME_ROOMS = dict()
def create_game(data):
    player = get_player(data)
    opponent_name = data["opponent_name"]
    game_name = data["game_name"]

    if game_name in GAME_ROOMS:
        raise SelectionError("Game Already Exists")
    game = NumberGame(player.name, opponent_name)
    GAME_ROOMS[game_name] = GameRoom(game, game_name)
    LOBBY.set_game_data()

def set_game(data):
    player = get_player(data)
    game_name = data["game_name"]
    game_room = GAME_ROOMS[game_name]
    player.join_game_room(game_room)
    LOBBY.remove_player(player)

@app.route('/')
def index():
    return render_template('lobby.html')

@app.route('/game')
def game():
    return render_template('game.html')

@app.route("/set_username", methods=["POST"])
def set_username():
    data = request.get_json()
    
    create_session(data)
    try:
        create_player(data)
    except SelectionError:
        pass
    
    set_player(data)
    connect(data)

    return jsonify({"success": True})

@socketio.on('reconnect')
def reconnect(data):
    connect(data)

@socketio.on('create_game')
def create_game_server(data):
    create_game(data)

@socketio.on('join_game')
def join_game_server(data):
    set_game(data)

@socketio.on('check_selection')
def check_selection_server(data):
    player = get_player(data)
    player.validate_turn(data)

@socketio.on('send_move')
def send_move_server(data):
    player = get_player(data)
    player.do_turn(data)

@socketio.on('update_state')
def update_state_server(data):
    player = get_player(data)
    player.set_state()

@socketio.on('on_game_load')
def on_game_load(data):
    player = get_player(data)
    player.on_load_game()
    player.set_state()

# TODO: 
@socketio.on('get_players')
def get_players_server(data):
    lobby = LOBBY
    player = get_player(data)

    lobby.set_player_data(player)

# TODO: 
@socketio.on('get_games')
def get_games_server(data):
    lobby = LOBBY
    player = get_player(data)

    lobby.set_game_data(player)


if __name__ == '__main__':
    print("Running on port 5000")
    socketio.run(app, host='0.0.0.0', port=5000)




