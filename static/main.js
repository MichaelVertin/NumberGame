const NAME_SELF = "BOB";
const NAME_OPPONENT = "ALICE";
const socket = io();

// button initialization after DOM loaded
document.addEventListener("DOMContentLoaded", () => {
  // set up sendMove button
  document.getElementById("sendMove").onclick = function () {
    const selections = get_selections();
    set_status_message("Sending Move...");
    socket.emit("send_move", selections);
  };

  socket.emit("update_state");
});

// card access /////////////////////////////////////////////////////////
function get_card_id(owner,index) {
  return { owner, index };
}

function get_card_obj(card_id) {
  const cards = get_cards(card_id.owner);
  return cards[card_id.index];
}

function get_field_container(owner_name) {
  let field_name = "";
  if(owner_name == NAME_SELF) {
    field_name = ".play-field-self";
  }
  else {
    field_name = ".play-field-opponent";
  }
  const container = document.querySelector(field_name);
  return container;
}

function get_cards(owner_name) {
  const container = get_field_container(owner_name);
  return container.querySelectorAll("button");
}

// card data access /////////////////////////////////////////////////////
function get_card_value(card_id) {
  var card_obj = get_card_obj(card_id);
  return card_obj.textContent;
}

function set_card_value(card_id,value) {
  var card_obj = get_card_obj(card_id);
  card_obj.textContent = value;
}

// card selection ///////////////////////////////////////////////////////
function get_owner(player_id) {
  if(player_id==0) {
    return NAME_OPPONENT;
  }
  return NAME_SELF;
}


// called when user clicks on a card
// toggles whether the card is selected
function select_card(index, owner) {
  let owner_name = owner;

  let card_id = get_card_id(owner_name,index);
  let card_obj = get_card_obj(card_id);

  const isSelected = card_obj.getAttribute("data-selected") == "true";
  card_obj.setAttribute("data-selected", !isSelected);

  // automatically check selection
  check_selection();
}

function select_deck() {
  const deck_obj = document.getElementById("deck");
  const isSelected = deck_obj.getAttribute("data-selected") == "true";

  deck_obj.setAttribute("data-selected", !isSelected);
  check_selection();
}

function check_selection() {
  const selected_cards = get_selections(); 
  set_status_message("Verifying Selection...");
  socket.emit("check_selection", selected_cards);
}

function get_selections() {
  let deck_selected = false;
  let card_selected = false;

  const deck_obj = document.getElementById("deck");
  if (deck_obj.getAttribute("data-selected") == "true") {
    deck_selected = true;
  }

  const cards = {
	          [NAME_SELF]: [], 
	          [NAME_OPPONENT]: []
                };
  get_cards(NAME_SELF).forEach((card_obj, index) => {
    const isSelected = card_obj.dataset.selected == "true";
    if(isSelected) {
      const card_id = get_card_id(NAME_SELF, index);
      cards[NAME_SELF].push(card_id);
      card_selected = true;
    }
  });

  get_cards(NAME_OPPONENT).forEach((card_obj, index) => {
    const isSelected = card_obj.dataset.selected == "true";
    if(isSelected) {
      const card_id = get_card_id(NAME_OPPONENT, index);
      cards[NAME_OPPONENT].push(card_id);
      card_selected = true;
    }
  });
  
  if (deck_selected && card_selected) {
    set_status_message("To draw, only select deck");
    return {"type": "none"};
  }
  if (deck_selected) {
    return {"type": "draw"}
  }

  return {"type": "attack", 
	  "cards": cards}
}

socket.on('set_selection_status', (response) => {
  if(response.status=="True") {
    set_status_message("Success: " + response.message);
  }
  else {
    set_status_message("Failed: " + response.message);
  }
});

// update game state
socket.on('set_state', (data) => {
  const cards = data.cards;
  const container_self = get_field_container(NAME_SELF);
  const container_opponent = get_field_container(NAME_OPPONENT);

  container_self.innerHTML = "";
  container_opponent.innerHTML = "";

  cards.forEach(card => {
    const button = document.createElement("button");
    button.className = "textbox";
    button.setAttribute("onclick", `select_card(${card.index}, "${card.owner}")`);
    button.innerHTML = card.value;
    const container = get_field_container(card.owner);
    container.appendChild(button);
  });

  set_turn(data.active_player);
  set_score(data.score);
});

function set_status_message(message) {
  const message_field = document.getElementById("status-message");
  message_field.innerHTML = message; 
}

function set_turn(player_name) {
  const name_field_self = document.querySelector('.name-self');
  const name_field_opponent = document.querySelector('.name-opponent');

  let name_field_active = "";
  let name_field_inactive = "";
  if (player_name == NAME_SELF) {
    name_field_active = name_field_self;
    name_field_inactive= name_field_opponent;
  }
  else {
    name_field_active = name_field_opponent;
    name_field_inactive = name_field_self;
  }

  name_field_active.classList.add("active-player");
  name_field_inactive.classList.remove("active-player");
}

function set_score(score) {
  const name_field_self = document.querySelector('.name-self');
  const name_field_opponent = document.querySelector('.name-opponent');

  name_field_self.innerText = NAME_SELF + ": " + score[NAME_SELF];
  name_field_opponent.innerText = NAME_OPPONENT + ": " + score[NAME_OPPONENT];
}





