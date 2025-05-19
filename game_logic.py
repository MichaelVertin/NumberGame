

class Card:
    def __init__(self, initial_value = "DEFAULT"):
        self.__value = initial_value

    def set_value(self, value):
        self.__value = value

    def get_value(self):
        return self.__value


class NumberGame:
    def __init__(self, player_name_one, player_name_two):
        self.__player_one_name = player_name_one 
        self.__player_two_name = player_name_two 
        self.__cards = dict()
        self.__cards[player_name_one] = list()
        self.__cards[player_name_two] = list()

        # start with three cards
        for card_ind in range(3):
            self.add_card(player_name_one)
            self.add_card(player_name_two)

    # returns the card object for the specified card
    def get_card_obj(self, card_id):
        return self.__cards[card_id["owner"]][card_id["index"]]

    # adds a new card to the owner's collection
    def add_card(self, owner, initial_value = "DEFAULT"):
        self.__cards[owner].append(Card(initial_value))

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
                card_state["value"] = card_obj.get_value()
                card_states.append(card_state)
        return card_states

    def submit_turn(self, selected_cards):
       turn_status = self.check_turn(selected_cards)
       if turn_status["status"] != "True":
           return turn_status
 
       return {"status": "False", "message": "Turn Submission not Implemented"}
 




