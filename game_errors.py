


class GameError (Exception):
    def __init__(self, message):
        super().__init__(message)

class CardNotExists (GameError):
    def __init__(self, card_id):
        self.card_id = card_id
        super().__init__(f"Referenced Card Does Not Exist {card_id}")

class SelectionError (GameError):
    def __init__(self, message):
        super().__init__(message)

class PlayerNotExists (GameError):
    def __init__(self, player_name):
        self.player = player_name
        super().__init__(f"Player '{player_name}' does not exist")





