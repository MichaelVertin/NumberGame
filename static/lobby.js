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
  socket.emit("reconnect", {session_id: SESSION_ID})
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
  remove_game_results();
  Object.entries(data).forEach(([game_name, game_info]) => {
    add_game_result(game_name, game_info.player1, game_info.player2);
  });
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

function add_game_result(game_name, player1, player2) {
console.log(game_name, player1, player2);
  const container = document.getElementById("existing-game-results");

  const button = document.createElement("button");
  button.className = "game-result";
  button.setAttribute("onclick", `select_game("${game_name}")`);

  // First line with game name
  const gameNameDiv = document.createElement("div");
  gameNameDiv.textContent = game_name;
  button.appendChild(gameNameDiv);

  // Player info container
  const playerContainer = document.createElement("div");

  const player1Div = document.createElement("div");
  player1Div.className = "game-player";
  player1Div.innerHTML = `<div>Player 1</div><div>${player1}</div>`;

  const player2Div = document.createElement("div");
  player2Div.className = "game-player";
  player2Div.innerHTML = `<div>Player 2</div><div>${player2}</div>`;

  playerContainer.appendChild(player1Div);
  playerContainer.appendChild(player2Div);

  button.appendChild(playerContainer);
  container.appendChild(button);
}

function remove_game_results() {
  const container = document.getElementById("existing-game-results");
  container.innerHTML = ""; // Clear all children
}

function select_game(game_name) {
  socket.emit("join_game", {"game_name": game_name, 
                            "session_id": SESSION_ID });
}

socket.off('disconnect');
socket.on('disconnect', () => {
  alert("An Unexpected Server Error Occurred");
});

socket.off('force_disconnect');
socket.on('force_disconnect', () => {
  my_alert("Another Player Has Accessed This Account", () => {
    window.location.href = "/";
  });
});

// alert is not blocking in force_disconnect
// this function was made with the help of chatgpt to force javascript
//   to wait for the user to respond to the alert before continuing
function my_alert(message, callback) {
  const modalOverlay = document.createElement("div");
  modalOverlay.style.cssText = `
    position: fixed;
    top: 0; left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(0,0,0,0.5);
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
  `;

  const modalBox = document.createElement("div");
  modalBox.style.cssText = `
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.5);
    text-align: center;
  `;

  modalBox.innerHTML = `
    <p style="margin-bottom: 15px;">${message}</p>
    <button id="alert-ok-btn" style="
      padding: 8px 20px;
      font-size: 1em;
    ">OK</button>
  `;

  modalOverlay.appendChild(modalBox);
  document.body.appendChild(modalOverlay);

  document.getElementById("alert-ok-btn").addEventListener("click", () => {
    document.body.removeChild(modalOverlay);
    callback(); // safely redirects after modal is removed
  });
}
