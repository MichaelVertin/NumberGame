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
  set_status_message("Checking...");
  check_selection();
}

function check_selection() {
  const selected_cards = get_selections(); 
  socket.emit("check_selection", selected_cards);
}

function get_selections() {
  const selected_cards = [];

  get_cards(NAME_SELF).forEach((card_obj, index) => {
    const isSelected = card_obj.dataset.selected == "true";
    if(isSelected) {
      const card_id = get_card_id(NAME_SELF, index);
      selected_cards.push(card_id);
    }
  });

  get_cards(NAME_OPPONENT).forEach((card_obj, index) => {
    const isSelected = card_obj.dataset.selected == "true";
    if(isSelected) {
      const card_id = get_card_id(NAME_OPPONENT, index);
      selected_cards.push(card_id);
    }
  });

  return selected_cards;
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
socket.on('set_state', (cards) => {
  const container_self = get_field_container(NAME_SELF);
  const container_opponent = get_field_container(NAME_OPPONENT);

  container_self.innerHTML = "";
  container_opponent.innerHTML = "";

  cards.forEach(card => {
    const button = document.createElement("button");
    button.className = "textbox";
    button.setAttribute("onclick", `select_card(${card.index}, "${card.owner}")`);
    button.textContent = card.value;
    const container = get_field_container(card.owner);
    container.appendChild(button);
  });
});

function set_status_message(message) {
  const message_field = document.getElementById("status-message");
  message_field.innerText = message; 
}


