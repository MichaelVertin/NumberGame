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


class NumberGame:
    def __init__(self, player_one_name, player_two_name, max_cards = 10):
        self.__cards = dict()
        self.__cards[player_one_name] = list()
        self.__cards[player_two_name] = list()
        self.__players = [player_one_name,player_two_name]
        self.__turn_count = 0
        self.__max_cards = max_cards
        self.__scores = {player_name:0 for player_name in self.__players}

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

    def get_state(self):
        card_states = list()
        for player_name in self.__players: 
            for card_index, card_obj in enumerate(self.__cards[player_name]):
                card_state = dict()
                card_state["owner"] = player_name
                card_state["index"] = card_index
                card_state["value"] = str(card_obj)
                card_states.append(card_state)
        return card_states

    def check_turn(self, selected_cards):
        active_cards = list()
        inactive_cards = list()
        deck_selected = False
        active_player = self.get_active_player()
        for card_id in selected_cards:
            if card_id.get("type") == "deck":
                deck_selected = True
                continue
            
            card_obj = self.get_card_obj(card_id)
            if card_id["owner"] == active_player:
                active_cards.append(card_id)
            else:
                inactive_cards.append(card_id)
        if deck_selected:
            if active_cards or inactive_cards:
                raise SelectionError("To draw cards, only select the deck")
            return {"status": "True", "message": "Draw Two Cards Selected"}

        active_value = sum([self.get_card_obj(card).offense for card in active_cards])
        inactive_value = sum([self.get_card_obj(card).defense for card in inactive_cards])
        if len(inactive_cards) != 1:
            raise SelectionError("Select exactly one of the opponent's cards")
        if len(active_cards) == 0:
            raise SelectionError("Select at least one of your cards")
        if active_value < inactive_value:
            raise SelectionError("Your value is not large enough")
        return {"status": "True", "message": "Selections are Valid"}





    def submit_turn(self, selected_cards):
        self.check_turn(selected_cards)
        if len(selected_cards) == 1:
            active_player = self.get_active_player()
            for i in range(2):
                self.add_card(active_player)
        else:
            # add to score
            active_player = self.get_active_player()
            active_cards = [card for card in selected_cards if card["owner"]==active_player]
            active_cards = [self.get_card_obj(card_id) for card_id in active_cards]
            for card_obj in active_cards:
                self.__scores[active_player] += card_obj.value

            # remove all selected cards
            for card_id in selected_cards:
                self.__cards[card_id["owner"]][card_id["index"]] = None
            for player_name in self.__players:
                self.__cards[player_name] = [card for card in self.__cards[player_name] \
                                              if card != None]
        
        # add a card to each player
        for player_name in self.__players:
            for card_count in range(CARDS_PER_TURN):
                self.add_card(player_name)

        self.__turn_count += 1
        return {"status": "True", "message": "Turn Submitted Successfully"}

    def get_active_player(self):
        active_player = self.__players[self.__turn_count % len(self.__players)]
        return active_player

    def get_score(self):
        return self.__scores





