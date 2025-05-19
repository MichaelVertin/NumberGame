import random


class Card:
    def __init__(self, initial_value = None):
        self.value = random.randint(0,100)

    def __str__(self):
        return str(self.value)


class NumberGame:
    def __init__(self, player_name_one, player_name_two):
        self.__player_one_name = player_name_one 
        self.__player_two_name = player_name_two 
        self.__cards = dict()
        self.__cards[player_name_one] = list()
        self.__cards[player_name_two] = list()
        self.__players = [self.__player_one_name,self.__player_two_name]
        self.__turn_count = 0

        # start with three cards
        for card_ind in range(3):
            self.add_card(player_name_one)
            self.add_card(player_name_two)

    # returns the card object for the specified card
    def get_card_obj(self, card_id):
        return self.__cards[card_id["owner"]][card_id["index"]]

    # adds a new card to the owner's collection
    def add_card(self, owner):
        self.__cards[owner].append(Card())

    def check_turn(self, selected_cards):
        try:
            for card_id in selected_cards:
                card = self.get_card_obj(card_id)
            return {"status": "True", "message": "All Selected Cards Exist"} 
        except IndexError:
            return {"status": "False", "message": "Card does not exist"}

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

    def submit_turn(self, selected_cards):
        turn_status = self.check_turn(selected_cards)
        if turn_status["status"] != "True":
            return turn_status
        
        active_cards = list()
        inactive_cards = list()
        active_player = self.__players[self.__turn_count % len(self.__players)]
        for card_id in selected_cards:
            card_obj = self.get_card_obj(card_id)
            if card_id["owner"] == active_player:
                active_cards.append(card_id)
            else:
                active_cards.append(card_id)
        active_value = sum([self.get_card_obj(card).value for card in active_cards])
        inactive_value = sum([self.get_card_obj(card).value for card in inactive_cards])

        if active_value < inactive_value:
            return {"status": "False", "message": "Value not Large Enough"}
        
        # remove all selected cards
        for card_id in active_cards + inactive_cards:
            del self.__cards[card_id["owner"]][card_id["index"]]
        self.__turn_count += 1

        for player_name in self.__players:
            self.add_card(player_name)

        return {"status": "True", "message": "Turn Submitted Successfully"}
 




