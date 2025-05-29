import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, session, jsonify
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

# TODO: Delete session on disconnect
class Session:
    def __init__(self, session_id):
        self.session_id = session_id
        self.sid = None
        self.player = None
        self.connect()

    def set_player(self, player):
        self.player = player

    def get_player(self):
        if not self.player: raise SelectionError("Session Has No Associated Player")
        return self.player

    def emit(self, method_name, data = None):
        if data:
            emit(method_name, data, to=self.sid)
        else:
            emit(method_name, to=self.sid)

    # NOTE: Only works when called from socketio.on
    def connect(self):
        try:
            self.sid = request.sid
        except:
            self.sid = None


class Player:
    def __init__(self, player_name):
        self.name = player_name
        self.session = None
        self.game_room = None

    def connect(self, session):
        # TODO: Disconnect previous session
        self.session = session
    
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


# session access
SESSIONS = dict()
def create_session(data):
    session_id = data["session_id"]
    SESSIONS[session_id] = Session(session_id)

def get_session(data):
    session_id = data["session_id"]
    if session_id not in SESSIONS:
        SESSIONS[session_id] = Session(session_id)
    return SESSIONS[session_id]

def connect(data):
    session = get_session(data)
    session.connect()
    # connect player to session if applicable
    try:
        player = get_player(data)
        player.connect(session)
    except SelectionError:
        pass

# player access
PLAYERS = dict()
def create_player(data):
    player_name = data["username"]
    if player_name in PLAYERS:
        raise SelectionError("Player Already Exists")
    PLAYERS[player_name] = Player(player_name)

def get_player(data):
    session = get_session(data)
    return session.get_player()

def set_player(data):
    session = get_session(data)
    player_name = data["username"]
    player = PLAYERS[player_name]
    
    session.set_player(player)
    player.connect(session)

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

def set_game(data):
    player = get_player(data)
    game_name = data["game_name"]
    game_room = GAME_ROOMS[game_name]
    player.join_game_room(game_room)



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
    players = PLAYERS
    player_data = dict()
    player_self = get_player(data)
    for player_name, player in players.items():
        player_data[player_name] = {}
        player_data[player_name]["is_you"] = str(player_self.name == player_name)

    emit("set_players", player_data)

# TODO: 
@socketio.on('get_games')
def get_games_server(data):
    rooms = GAME_ROOMS
    your_player = get_player(data)
    game_data = dict()
    for game_name, game_room in rooms.items():
        player_names = game_room.get_players()
        your_game = your_player.name in player_names
        game_item = {"player1": player_names[0],
                     "player2": player_names[1],
                     "your_game": your_game}
        game_data[game_name] = game_item

    emit("set_games", game_data)


if __name__ == '__main__':
    print("Running on port 5000")
    socketio.run(app, host='0.0.0.0', port=5000)




