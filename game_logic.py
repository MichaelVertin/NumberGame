import random


class Card:
    def __init__(self, initial_value = None):
        self.value = random.randint(10,100)

    def __str__(self):
        return str(self.value)


class NumberGame:
    def __init__(self, player_name_one, player_name_two, max_cards = 10):
        self.__player_one_name = player_name_one 
        self.__player_two_name = player_name_two 
        self.__cards = dict()
        self.__cards[player_name_one] = list()
        self.__cards[player_name_two] = list()
        self.__players = [self.__player_one_name,self.__player_two_name]
        self.__turn_count = 0
        self.__max_cards = max_cards

        # start with three cards
        for player_name in self.__players:
            for card_ind in range(3):
                self.add_card(player_name)

    # returns the card object for the specified card
    def get_card_obj(self, card_id):
        try:
            cards = self.__cards[card_id["owner"]]
        except:
            raise ValueError(f"No player named {card_id['owner']}")
        try:
            card_obj = cards[card_id["index"]]
        except:
            raise ValueError(f"Selected card does not exist")
        return card_obj 

    # adds a new card to the owner's collection
    def add_card(self, owner):
        if len(self.__cards[owner]) >= self.__max_cards: return False
        self.__cards[owner].append(Card())
        return True

    def get_state(self):
        card_states = list()
        for player_name in [self.__player_one_name,self.__player_two_name]:
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
        active_player = self.__players[self.__turn_count % len(self.__players)]
        for card_id in selected_cards:
            card_obj = self.get_card_obj(card_id)
            if card_id["owner"] == active_player:
                active_cards.append(card_id)
            else:
                inactive_cards.append(card_id)
        active_value = sum([self.get_card_obj(card).value for card in active_cards])
        inactive_value = sum([self.get_card_obj(card).value for card in inactive_cards])
        if len(inactive_cards) != 1:
            raise ValueError("Select exactly one of the opponent's cards")
        if len(active_cards) == 0:
            raise ValueError("Select at least one of your cards")
        if active_value < inactive_value:
            raise ValueError("Your value is not large enough")
        return {"status": "True", "message": "Selections are Valid"}





    def submit_turn(self, selected_cards):
        self.check_turn(selected_cards)

        # remove all selected cards
        for card_id in selected_cards:
            self.__cards[card_id["owner"]][card_id["index"]] = None
        for player_name in self.__players:
            self.__cards[player_name] = [card for card in self.__cards[player_name] \
                                              if card != None]
        
        # add a card to each player
        for player_name in self.__players:
            self.add_card(player_name)
        
        self.__turn_count += 1

        return {"status": "True", "message": "Turn Submitted Successfully"}
 




