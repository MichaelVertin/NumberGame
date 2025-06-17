import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from game_logic import *
from session import Session
from player import Player
from game_room import GameRoom

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret'
socketio = SocketIO(app, async_mode='eventlet')


class Lobby:
    def __init__(self):
        self.__players = list()

    def add_player(self, player):
        self.__players.append(player)
    
    def remove_player(self, player):
        self.__players.remove(player)

    def get_player_data(self):
        return PlayerHandler.get_player_data()

    def get_game_data(self):
        game_data = GameRoomHandler.get_room_data()
        return game_data

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




class SessionManager:
    _sessions = dict()

    # gets the specified player
    # creates a new session
    # connects the session and the player
    @classmethod
    def initialize_session(cls, data):
        session_id = data["session_id"]
        player_id = data["username"]
        print(f"Initializing Session: {session_id}")

        # retrieve the player
        # TODO: move player creation elsewhere
        try:
            player = PlayerHandler.create(data)
        except SelectionError:
            player = PlayerHandler.get(data)

        # disconnect the active session
        prev_session = player.abandon_session()
        if prev_session:
            print(f"Disconnecting Session: {prev_session.get_id()}")
            del cls._sessions[prev_session.get_id()]
            prev_session.disconnect(message="Another session was established for this player")

        session = Session(data, socketio)
        player.set_session(session)
        session.set_player(player)

        cls._sessions[session_id] = session

    # updates the socketio data for the active session
    @classmethod
    def on_page_load(cls, data):
        print(f"Reconnecting Session: {data['session_id']}")
        session = cls.get(data)
        session.update(data)

    # get the active session
    @classmethod
    def get(cls, data):
        session_id = data["session_id"]
        print(f"Accessing Session: {session_id}")
        session = cls._sessions.get(session_id)
        if not session: raise SelectionError(f"Session {session_id} is not recongnized")
        return session

    # get the player for the active session
    @classmethod
    def get_player(cls, data):
        session = cls.get(data)
        return session.get_player()


class PlayerHandler:
    _players = dict()
    
    @classmethod
    def create(cls, data):
        player_name = data["username"]
        
        # fail if player already exists
        if player_name in cls._players:
            raise SelectionError("Player Already Exsits")
        
        # store a new player object
        player = Player(player_name)
        cls._players[player_name] = player
        
        # start the player in the lobby
        LOBBY.add_player(player)
        return player

    @classmethod
    def get_player_data(cls):
        player_data = dict()
        for player_name, player in cls._players.items():
            player_data[player_name] = {}

        return player_data

    @classmethod
    def get(cls, data):
        player_name = data["username"]
        if player_name not in cls._players:
            raise SelectionError("Player Does Not Exist")

        return cls._players[player_name]


class GameRoomHandler:
    _rooms = dict()
    
    @classmethod
    def create(cls, data):
        # set Player1 to the player's name, and Player2 to the opponent's name
        player = SessionManager.get_player(data)
        opponent_name = data["opponent_name"]
        game_name = data["game_name"]

        # fail if the game_name already exists
        if game_name in cls._rooms:
            raise SelectionError("Game Already Exists")
        
        # create the game and game_room
        game = NumberGame(player.name, opponent_name)
        cls._rooms[game_name] = GameRoom(game, game_name)
        
        # update the lobby's game content
        LOBBY.set_game_data()

    @classmethod
    def get(cls, data):
        game_name = data["game_name"]
        game_room = cls._rooms.get(game_name)
        return game_room

    @classmethod
    def join_game(cls, data):
        player = SessionManager.get_player(data)
        game_room = cls.get(data)
        
        # move player from the lobby to the game
        player.join_game_room(game_room)
        LOBBY.remove_player(player)

    @classmethod
    def get_room_data(cls):
        game_data = dict()
        for game_name, game_room in cls._rooms.items():
            player_names = game_room.get_players()
            game_data[game_name] = {
                    "player1": player_names[0], 
                    "player2": player_names[1]
            }
        return game_data

# lobby
LOBBY = Lobby()



@app.route('/')
def index():
    return render_template('lobby.html')

@app.route('/game')
def game():
    return render_template('game.html')

@app.route("/set_username", methods=["POST"])
def set_username():
    data = request.get_json()
    SessionManager.initialize_session(data)
    
    return jsonify({"success": True})

@socketio.on('reconnect')
def reconnect(data):
    SessionManager.on_page_load(data)

@socketio.on('create_game')
def create_game(data):
    GameRoomHandler.create(data)

@socketio.on('join_game')
def join_game(data):
    GameRoomHandler.join_game(data)

@socketio.on('check_selection')
def check_selection(data):
    player = SessionManager.get_player(data)
    player.validate_turn(data)

@socketio.on('send_move')
def send_move(data):
    player = SessionManager.get_player(data)
    player.do_turn(data)

@socketio.on('update_state')
def update_state(data):
    player = SessionManager.get_player(data)
    player.set_state()

@socketio.on('on_game_load')
def on_game_load(data):
    player = SessionManager.get_player(data)
    player.on_load_game()
    player.set_state()

@socketio.on('get_players')
def get_players_server(data):
    player = SessionManager.get_player(data)

    LOBBY.set_player_data(player)

@socketio.on('get_games')
def get_games_server(data):
    player = SessionManager.get_player(data)

    LOBBY.set_game_data(player)


if __name__ == '__main__':
    print("Running on port 5000")
    socketio.run(app, host='0.0.0.0', port=5000)



