


# User Defined Error:
# If any component is capable of producing an error, that error must inherit from LogicError
class LogicError (Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"


# Session Error:
#  Raised when an issue relating to a session is caught
class SessionError (LogicError):
    def __init__(self, message = "A session error occurred"):
        super().__init__(message)

# Session Creation Error:
#  Raised when the session cannot be created
class SessionCreationError (SessionError):
    def __init__(self, message = "An error occurred attempting to create the session"):
        super().__init__(message)

# Session Access Error:
#  Raised when the session cannot be accessed
class SessionAccessError (SessionError):
    def __init__(self, message = "An error occurred attempting to access the session"):
        super().__init__(message)

# Session Not Established Error: 
#  Raised when accessing the active session before initialization
class SessionNotEstablishedError (SessionAccessError):
    def __init__(self, message = "No session was established"):
        super().__init__(message)

# Player Has No Session Error:
#  Raised when a player has no associated session
class PlayerHasNoSessionError (SessionAccessError):
    def __init__(self, player_name):
        super().__init__(f"No session associated with player {player_name}")

# Invalid Move Error:
#  Raised when a move is not allowed
class InvalidMoveError (LogicError):
    def __init__(self, message = "This move is invalid"):
        super().__init__(message)

# Move Not Recognized Error
#  Raised when the move type is invalid
class MoveNotRecongizedError (InvalidMoveError):
    def __init__(self, move_label):
        super().__init__(f"Move type {move_label} not recongized")

# Not Active Player Error:
#  Raised when an inactive player tries to validate their turn
class NotActivePlayerError (InvalidMoveError):
    def __init__(self):
        super().__init__(f"Not your turn")

# Player Already Exists Error
#  Raised when attempting to create a player, but it already exists
class PlayerAlreadyExistsError (LogicError):
    def __init__(self, player_name):
        super().__init__(f"Player {player_name} already exists")

# Player Does Not Exist Error
#  Raised when accessing a player, but does not exist
class PlayerDoesNotExistError (LogicError):
    def __init__(self, player_name):
        super().__init__(f"Player {player_name} does not exist")
        

# Game Already Exists Error
#  Raised when attempting to create a game, but it already exists
class GameAlreadyExistsError (LogicError):
    def __init__(self, game_name):
        super().__init__(f"Game {game_name} already exists")

# Game Does Not Exist Error
#  Raised when accessing a game, but does not exist
class GameDoesNotExistError (LogicError):
    def __init__(self, game_name):
        super().__init__(f"Game {game_name} does not exist")
        

