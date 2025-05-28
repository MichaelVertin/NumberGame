import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, session, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from game_logic import *

class Player:
    def __init__(self, player_name, sid):
        self.name = player_name
        self.sid = sid

    def join_game(self, game_room):
        self.game_room = game_room
        emit("load_game", to=self.sid)

    def get_game_room(self):
        return self.game_room

    def update_state(self):
        self.get_game_room().update_player(self)

    def do_turn(self, data):
        try:
            self.game_room.do_turn(self, data)
            emit('set_selection_status', {"status": "True", "message": "Turn Completed Successfully"}, to=self.sid)

        except SelectionError as e:
            emit('set_selection_status', {"status": "False", "message":str(e)}, to=self.sid)

    def check_turn(self, data):
        try:
            game_room = self.get_game_room()
            status = game_room.check_turn(self, data)
            emit('set_selection_status', status)
        except SelectionError as e:
            emit('set_selection_status', {"status": "False", "message":str(e)}, to=self.sid)
             
    def reconnect(self, sid):
        self.sid = sid
        game_room = self.get_game_room()
        if game_room:
            game_room.reconnect_player(self)
            self.set_names()

    def set_names(self):
        players = self.get_game_room().get_players()
        your_name = self.name
        if your_name not in players:
            your_name = players[0]

        data = dict()
        data["your_name"] = your_name
        data["other_names"] = [name for name in players if name != your_name]
        emit('set_names', data, to=self.sid)


class GameRoom:
    def __init__(self, game, name):
        self.__game = game
        self.__room_id = name

    def do_turn(self, player, data):
        if self.__game.get_active_player() != player.name:
            raise SelectionError("Not Your Turn")
        turn_obj = get_turn_obj(data, self.__game)
        status = turn_obj.execute()
        self.update_players()

    def check_turn(self, player, data):
        if self.__game.get_active_player() != player.name:
            raise SelectionError("Not Your Turn")
        turn_obj = get_turn_obj(data, self.__game)
        status = turn_obj.validate()
        return status

    def add_player(self, player):
        if player.sid:
            join_room(self.__room_id, sid=player.sid)
            # TODO: This is never called

    def reconnect_player(self, player):
        if player.sid:
            join_room(self.__room_id, sid=player.sid)

    def remove_player(self, player):
        leave_room(self.__room_id, sid=player.sid)

    def update_players(self):
        game = self.__game
        state = game.get_state()
        emit('set_state', state, room=self.__room_id)

    def update_player(self, player):
        game = self.__game
        state = game.get_state()
        emit('set_state', state, to=player.sid)

    def get_players(self):
        return [self.__game.get_active_player(), self.__game.get_inactive_player()]

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret'
socketio = SocketIO(app, async_mode='eventlet')

GAME_ROOMS = dict()
PLAYERS = dict()
PLAYER_SESSION_DATA = dict()


def get_turn_obj(data, game):
    if data["type"] == "draw":
        turn_obj = Turn_Draw(game)
    elif data["type"] == "attack":
        turn_obj = Turn_Attack(game, 
                              data["cards"])
    else:
        raise SelectionError("To draw, only select the deck") # TODO # implement this into javascript
    return turn_obj

def get_sid():
    try:
        return request.sid
    except:
        pass
    return None




# API
@app.route('/')
def index():
    return render_template('lobby.html')

@app.route('/game')
def game():
    return render_template('game.html')

@app.route("/set_username", methods=["POST"])
def set_username():
    sid = get_sid()
    data = request.get_json()
    username = data["username"]
    # session["username"] = username
    session_id = data["session_id"]
    PLAYER_SESSION_DATA[session_id] = username
    PLAYERS[username] = Player(username, sid)
    return jsonify({"success": True})

def get_player(session_id):
    username = PLAYER_SESSION_DATA[session_id]
    # username = session["username"]
    return PLAYERS[username]

@socketio.on('reconnect')
def reconnect(data):
    sid = get_sid()
    player = get_player(data["session_id"])
    player.reconnect(sid)

# TODO: incomplete
@socketio.on('create_game')
def create_game(data):
    player = get_player(data["session_id"])
    opponent_name = data["opponent_name"]
    game_name = data["game_name"]

    if game_name in GAME_ROOMS.keys():
        raise ValueError(f"Game {game_name} already exists")
    game = NumberGame(player.name, opponent_name)
    GAME_ROOMS[game_name] = GameRoom(game, game_name)

# TODO: incomplete
@socketio.on('join_game')
def join_game(data):
    player = get_player(data["session_id"])
    game_name = data["game_name"]
    game_room = GAME_ROOMS[game_name]
    player.join_game(game_room)

@socketio.on('check_selection')
def check_selection(data):
    player = get_player(data["session_id"])
    player.check_turn(data)

@socketio.on('send_move')
def send_move(data):
    player = get_player(data["session_id"])
    player.do_turn(data)

@socketio.on('update_state')
def update_state(data):
    player = get_player(data["session_id"])
    player.update_state()

@socketio.on('get_players')
def get_players(data):
    players = PLAYERS
    player_data = dict()
    player_self = get_player(data["session_id"])
    for player_name, player in players.items():
        player_data[player_name] = {}
        player_data[player_name]["is_you"] = str(player_self.name == player_name)
    
    emit("set_players", player_data, to=player_self.sid)

@socketio.on('get_games')
def get_games(data):
    rooms = GAME_ROOMS
    your_player = get_player(data["session_id"])
    game_data = dict()
    for game_name, game_room in rooms.items():
        player_names = game_room.get_players()
        your_game = your_player.name in player_names
        game_item = {"player1": player_names[0], 
                     "player2": player_names[1], 
                     "your_game": your_game}
        game_data[game_name] = game_item

    emit("set_games", game_data, to=your_player.sid)


if __name__ == '__main__':
    print("Running on port 5000")
    socketio.run(app, host='0.0.0.0', port=5000)




