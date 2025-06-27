import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from game_logic import *
from session import Session
from player import Player
from game_room import GameRoom
from game_errors import *

from handlers import SessionHandler, PlayerHandler, GameRoomHandler, LOBBY

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret'
socketio = SocketIO(app, async_mode='eventlet')

@app.route('/')
def index():
    return render_template('lobby.html')

@app.route('/game')
def game():
    return render_template('game.html')

@app.route("/set_username", methods=["POST"])
def set_username():
    data = request.get_json()
    SessionHandler.initialize_session(data)
    
    # TODO: Move this into PlayerHander.create()
    LOBBY.set_player_data()
    
    return jsonify({"success": True})

@socketio.on('reconnect')
def reconnect(data):
    SessionHandler.on_page_load(data)

@socketio.on('create_game')
def create_game(data):
    GameRoomHandler.create(data)

@socketio.on('join_game')
def join_game(data):
    GameRoomHandler.join_game(data)

@socketio.on('check_selection')
def check_selection(data):
    player = SessionHandler.get_player(data)
    player.validate_turn(data)

@socketio.on('send_move')
def send_move(data):
    player = SessionHandler.get_player(data)
    player.do_turn(data)

@socketio.on('update_state')
def update_state(data):
    player = SessionHandler.get_player(data)
    player.set_state()

@socketio.on('on_game_load')
def on_game_load(data):
    player = SessionHandler.get_player(data)
    player.on_load_game()
    player.set_state()

@socketio.on('get_players')
def get_players_server(data):
    player = SessionHandler.get_player(data)

    LOBBY.set_player_data(player)

@socketio.on('get_games')
def get_games_server(data):
    player = SessionHandler.get_player(data)

    LOBBY.set_game_data(player)

@socketio.on('disconnect')
def on_disconnect(sid):
    SessionHandler.disconnect_session(sid)
    print(SessionHandler._sessions)


@socketio.on_error_default
def socket_io_error_handle(e):
    if isinstance(e, LogicError):
        socketio.emit("on_error", {"message": str(e)})
        raise e
    else:
        socketio.emit("on_error", {"message": "An Unexpected Error Occurred"})
        raise e



if __name__ == '__main__':
    SessionHandler.init(socketio)
    print("Running on port 5000")
    socketio.run(app, host='0.0.0.0', port=5000)


