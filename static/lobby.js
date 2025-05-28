const socket = io();
let USERNAME = "";


// https://stackoverflow.com/questions/105034/how-do-i-create-a-guid-uuid
function uuidv4() {
  return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, c =>
    (+c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> +c / 4).toString(16)
  );
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

if (!sessionStorage.getItem("customSessionId")) {
  const newId = uuidv4();
  sessionStorage.setItem("customSessionId", newId);
}
const SESSION_ID = sessionStorage.getItem("customSessionId");

document.addEventListener("DOMContentLoaded", () => {
  USERNAME = prompt("Enter Your Name");
  const name_field = document.getElementById("name-field");
  name_field.innerHTML = USERNAME;

  const name_field2 = document.getElementById("your-name");
  name_field2.value = USERNAME;
  name_field2.disabled = true;

  create_player(USERNAME);

  // TODO? Wait for player to be created correctly
  set_games();
  set_players();
});

async function create_player(username) {
  const response = await fetch("/set_username", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ 
      username: username, 
      session_id: SESSION_ID 
    })
  });
}

function submit_new_game() {
  const game_name = document.getElementById("new-game-name").value;
  const opponent_name = document.getElementById("opponent-name").value;

  socket.emit("create_game", {"opponent_name": opponent_name, 
                              "game_name": game_name, 
                              "session_id": SESSION_ID }); 
}

function submit_existing_game() {
  const game_name = document.getElementById("filter-existing-game").value;
  
  socket.emit("join_game", {"game_name": game_name, 
                            "session_id": SESSION_ID });
}

socket.on("load_game", () => {
  window.location.href = "/game";
});

function set_games() {
  socket.emit("get_games", {session_id: SESSION_ID});
}

function set_players() {
  socket.emit("get_players", {session_id: SESSION_ID} );
}

socket.on("set_games", (data) => {
  const game_field = document.getElementById("existing-game-results");
  let data_to_display = "";
  Object.entries(data).forEach(([game_name, game_info]) => {
    data_to_display += `${game_name}: ${game_info.player1} & ${game_info.player2}`;
    if (game_info.your_game == "True") {
      data_to_display += " (Your Game)"; // TODO: Error: Does not work"
    }
    data_to_display += "<br>";
  });
  game_field.innerHTML = data_to_display;
});

socket.on("set_players", (data) => {
  const player_field = document.getElementById("player-results");
  let data_to_display = "";
  Object.entries(data).forEach(([player_name, player_info]) => {
    data_to_display += player_name;
    if (player_info.is_you == "True") {
      data_to_display += " (you)";
    }
    data_to_display += "<br>";
  });
  player_field.innerHTML = data_to_display;
});





