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

class GameRoom:
    def __init__(self, game, name):
        self.__game = game
        self.__room_id = name
        self.__players = dict()

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
        print("Adding player")
        if player.sid:
            join_room(self.__room_id, sid=player.sid)
            # TODO: This is never called
        self.__players[player.name] = player

    def reconnect_player(self, player):
        if player.sid:
            join_room(self.__room_id, sid=player.sid)
        self.__players[player.name] = player

    def remove_player(self, player):
        leave_room(self.__room_id, sid=player.sid)
        del self.__players[player.name]

    def update_players(self):
        game = self.__game
        state = game.get_state()
        active_player = game.get_active_player()
        score = game.get_score()
        state = {"cards": state, 
                 "active_player": active_player, 
                 "score": score}
        #for player_name, player in self.__players.items():
        #    emit('set_state', state, to=player.sid)
        emit('set_state', state, room=self.__room_id)
        # TODO: Error: this does not send the state to the client

    def update_player(self, player):
        game = self.__game
        state = game.get_state()
        score = game.get_score()
        active_player = game.get_active_player()
        state = {"cards": state, 
                 "active_player": active_player, 
                 "score": score}
        emit('set_state', state, to=player.sid)




app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret'
socketio = SocketIO(app, async_mode='eventlet')

GAME_ROOMS = dict()
PLAYERS = dict()

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
    data = request.get_json()
    sid = get_sid()
    username = data["username"]
    session["username"] = username
    PLAYERS[username] = Player(username, sid)
    return jsonify({"success": True})

def get_player():
    username = session["username"]
    return PLAYERS[username]

@socketio.on('reconnect')
def reconnect():
    sid = get_sid()
    player = get_player()
    player.reconnect(sid)

# TODO: incomplete
@socketio.on('create_game')
def create_game(data):
    player = get_player()
    opponent_name = data["opponent_name"]
    game_name = data["game_name"]

    if game_name in GAME_ROOMS.keys():
        raise ValueError("Game {game_name} already exists")
    game = NumberGame(player.name, opponent_name)
    GAME_ROOMS[game_name] = GameRoom(game, game_name)

# TODO: incomplete
@socketio.on('join_game')
def join_game(data):
    player = get_player()
    game_name = data["game_name"]
    game_room = GAME_ROOMS[game_name]
    player.join_game(game_room)

@socketio.on('check_selection')
def check_selection(data):
    player = get_player()
    player.check_turn(data)

@socketio.on('send_move')
def send_move(data):
    player = get_player()
    player.do_turn(data)

@socketio.on('update_state')
def update_state():
    player = get_player()
    player.update_state()


if __name__ == '__main__':
    print("Running on port 5000")
    socketio.run(app, host='0.0.0.0', port=5000)




