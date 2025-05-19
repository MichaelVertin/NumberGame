let NAME_SELF = "BOB";
let NAME_OPPONENT = "ALICE";

// temp for testing
document.addEventListener("DOMContentLoaded", () => {
  const socket = io();

  document.getElementById("confirmBtn").onclick = function () {
    socket.emit("confirm", { user: "Bob", selected: [42, 93] });
  };

  socket.on("server_response", (data) => {
    document.getElementById("message").innerText = data.message;
  });
});

function select_card(index, player_id) {
  let owner_name = get_owner(player_id);
  console.log(owner_name, "'s card selected:", index);
}

function get_card_id(owner,index) {
  return { owner, index };
}

function get_card_obj(card_id) {
  const buttons = document.querySelectorAll('.textbox');
  var index = card_id.get("index");
  var owner = card_id.get("owner");

  if(owner==NAME_SELF) {
    index += 10;
  }
  return buttons[index];
}

function get_card_value(card_id) {
  var card_obj = get_card_obj(card_id);
  return card_obj.textContent;
}

function set_card_value(card_id,value) {
  var card_obj = get_card_obj(card_id);
  card_obj.textContent = value;
}

function get_owner(player_id) {
  if(player_id==0) {
    return NAME_OPPONENT;
  }
  return NAME_SELF;
}



