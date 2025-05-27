import random
from game_errors import *

CARDS_PER_TURN = 1
OFFENSE_MIN = 5
OFFENSE_MAX = 10
DEFENSE_MIN = 15
DEFENSE_MAX = 30
VALUE_MIN = 3
VALUE_MAX = 7

class Card:
    def __init__(self, initial_value = None):
        self.offense = random.randint(OFFENSE_MIN,OFFENSE_MAX)
        self.defense = random.randint(DEFENSE_MIN,DEFENSE_MAX)
        self.value = random.randint(VALUE_MIN,VALUE_MAX)

    def __str__(self):
        return f"{self.offense} / {self.defense}<br>{self.value}"

class Turn:
    def __init__(self):
        raise NotImplementedError("Abstract Class")

    def execute(self):
        raise NotImplementedError("Abstract Class")

    def validate(self):
        raise NotImplementedError("Abstract Class")

class Turn_Draw(Turn):
    def __init__(self, game):
        self.game = game

    def execute(self):
        active_player = self.game.get_active_player()
        self.game.add_card(active_player)

        self.game.pass_turn()
        
        return {"status": "True", "message": "Succesfully Drew Cards"}

    def validate(self):
        return {"status": "True", "message": "Selected Deck Correctly"}

class Turn_Attack(Turn):
    def __init__(self, game, cards):
        self.game = game
        active_cards = cards[self.game.get_active_player()]
        inactive_cards = cards[self.game.get_inactive_player()]
        self.active_cards = [self.game.get_card_obj(card) for card in active_cards]
        self.inactive_cards = [self.game.get_card_obj(card) for card in inactive_cards]
        
        self.active_value = sum([card.offense for card in self.active_cards])
        self.inactive_value = sum([card.defense for card in self.inactive_cards])

    def execute(self):
        active_player = self.game.get_active_player()
        inactive_player = self.game.get_inactive_player()

        self.validate()
        self.game.remove_cards(active_player, self.active_cards)
        self.game.remove_cards(inactive_player, self.inactive_cards)
        self.game.add_points(active_player, self.inactive_value)

        self.game.pass_turn()
        return {"status": "True", "message": "Successfully Executed Attack"}

    def validate(self):
        if len(self.inactive_cards) != 1:
            raise SelectionError("Select exactly one of the opponent's cards")
        if len(self.active_cards) == 0:
            raise SelectionError("Select at least one of your cards")
        if self.active_value < self.inactive_value:
            raise SelectionError("Your value is not large enough")
        return {"status": "True", "message": "Selections are Valid"}




class NumberGame:
    def __init__(self, player_one_name, player_two_name, max_cards = 10):
        self.__players = [player_one_name,player_two_name]
        self.__max_cards = max_cards
        self.__scores = {player_name:0 for player_name in self.__players}
        self.__cards = {player_name: list() for player_name in self.__players}
        self.__turn_count = 0
        
        # start with three cards
        for player_name in self.__players:
            for card_ind in range(3):
                self.add_card(player_name)

    # returns the card object for the specified card
    def get_card_obj(self, card_id):
        try:
            cards = self.__cards[card_id["owner"]]
        except:
            raise PlayerNotExists(card_id["owner"])
        try:
            card_obj = cards[card_id["index"]]
        except:
            raise CardNotExists(card_id)
        return card_obj 

    # adds a new card to the owner's collection
    def add_card(self, owner):
        if len(self.__cards[owner]) >= self.__max_cards: return False
        self.__cards[owner].append(Card())
        return True

    def get_cards(self):
        card_states = list()
        for player_name in self.__players: 
            for card_index, card_obj in enumerate(self.__cards[player_name]):
                card_state = dict()
                card_state["owner"] = player_name
                card_state["index"] = card_index
                card_state["value"] = str(card_obj)
                card_states.append(card_state)
        return card_states 

    def get_state(self):
        cards = self.get_cards()
        score = self.get_score()
        active_player = self.get_active_player()
        state = {"cards": cards,
                 "active_player": active_player,
                 "score": score}
        return state

    def pass_turn(self):
        # add a card to each player
        for player_name in self.__players:
            for card_count in range(CARDS_PER_TURN):
                self.add_card(player_name)

        self.__turn_count += 1

    def remove_cards(self, player, card_objs):
        card_list = self.__cards[player]
        card_list = [card for card in card_list if card not in card_objs]
        self.__cards[player] = card_list

    def get_active_player(self):
        return self.__players[self.__turn_count % len(self.__players)]

    def get_inactive_player(self):
        return self.__players[(self.__turn_count + 1) % len(self.__players)]

    def get_score(self):
        return self.__scores

    def add_points(self, player, amount):
        self.__scores[player] += amount



