let NAME_SELF = "BOB";
let NAME_OPPONENT = "ALICE";
const socket = io();

// temp for testing
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("confirmBtn").onclick = function () {
    socket.emit("confirm", { user: "Bob", selected: [42, 93] });
  };

  socket.on("server_response", (data) => {
    document.getElementById("message").innerText = data.message;
  });
});




// card access /////////////////////////////////////////////////////////
function get_card_id(owner,index) {
  return { owner, index };
}

function get_card_obj(card_id) {
  const buttons = document.querySelectorAll('.textbox');
  

  var index = card_id.index;
  var owner = card_id.owner;

  if(owner==NAME_SELF) {
    index += 10;
  }
  return buttons[index];
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

function select_card(index, player_id) {
  let owner_name = get_owner(player_id);
  console.log(owner_name, "'s card selected:", index);

  let card_id = get_card_id(owner_name,index);
  let card_obj = get_card_obj(card_id);

  const isSelected = card_obj.getAttribute("data-selected") == "true";
  card_obj.setAttribute("data-selected", !isSelected);
  
  check_selection();
}


function check_selection() {
  const selected_cards = [];
  const buttons = document.querySelectorAll('.textbox');

  buttons.forEach((card_obj, ind) => {
    if (card_obj.dataset.selected == "true") {
      const index = ind % 10;
      const owner_id = Math.floor(ind / 10);
      const card_id = get_card_id(get_owner(owner_id), index);
      selected_cards.push(card_id);
    }
  });

  socket.emit("check_selection", selected_cards);
}


socket.on('set_selection_status', (response) => {
  if(response.status=="True") {
    console.log("Success:", response.message);
    socket.emit("update_state", {});
  }
  else {
    console.log("Fail:", response.message);
  }
});

// update game state
socket.on('set_state', (cards) => {
  console.log("Received cards:", cards);

  cards.forEach(card => {
    let card_id = card;
    set_card_value(card_id,card.value);
  });
});




