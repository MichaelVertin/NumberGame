from game_errors import *
from player import Player
from session import Session
from game_room import GameRoom
from game_logic import NumberGame


class PlayerHandler:
    _players = dict()
    
    @classmethod
    def create(cls, data):
        player_name = data["username"]
        
        # fail if player already exists
        if player_name in cls._players:
            raise PlayerAlreadyExistsError(player_name)
        
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
            raise PlayerDoesNotExistError(player_name)

        return cls._players[player_name]


class GameRoomHandler:
    _rooms = dict()
    
    @classmethod
    def create(cls, data):
        # set Player1 to the player's name, and Player2 to the opponent's name
        player = SessionHandler.get_player(data)
        opponent_name = data["opponent_name"]
        game_name = data["game_name"]

        # fail if the game_name already exists
        if game_name in cls._rooms:
            raise GameAlreadyExistsError(game_name)
        
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
        player = SessionHandler.get_player(data)
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



class SessionHandler:
    _sessions = dict()

    @classmethod
    def init(cls, socketio):
        cls.socketio = socketio

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
        except PlayerAlreadyExistsError:
            player = PlayerHandler.get(data)

        # disconnect the active session
        prev_session = player.abandon_session()
        if prev_session:
            print(f"Disconnecting Session: {prev_session.get_id()}")
            del cls._sessions[prev_session.get_id()]
            prev_session.disconnect(message="Another session was established for this player")

        session = Session(data, cls.socketio)
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
        if not session: raise SessionAccessError()
        return session

    # get the player for the active session
    @classmethod
    def get_player(cls, data):
        session = cls.get(data)
        return session.get_player()

    # disconnects a session
    # if data is provided, disconnects the session with its session_id
    # otherwise, disconnects the active session
    @classmethod
    def disconnect_session(cls, sid):
        session = None

        for session_id, session_obj in cls._sessions.items():
            if session_obj.is_active(sid):
                session = session_obj
                break
        
        if not session:
            pass # raise SessionDisconnectError()
        else:
            del cls._sessions[session]


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







# lobby
LOBBY = Lobby()





