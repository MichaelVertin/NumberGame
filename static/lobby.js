const socket = io();
let USERNAME = "";



document.addEventListener("DOMContentLoaded", () => {
  USERNAME = prompt("Enter Your Name");
  const name_field = document.getElementById("name-field");
  name_field.innerHTML = USERNAME;

  const name_field2 = document.getElementById("your-name");
  name_field2.value = USERNAME;
  name_field2.disabled = true;

  create_player(USERNAME);

  set_games();
  set_players();
});


async function create_player(username) {
  const response = await fetch("/set_username", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username: username}),
  });
}

function submit_new_game() {
  const game_name = document.getElementById("new-game-name").value;
  const opponent_name = document.getElementById("opponent-name").value;

  socket.emit("create_game", {"opponent_name": opponent_name, 
                              "game_name": game_name}); 
}

function submit_existing_game() {
  const game_name = document.getElementById("filter-existing-game").value;
  
  socket.emit("join_game", {"game_name": game_name});
}

socket.on("load_game", () => {
  window.location.href = "/game";
});

function set_games() {
  socket.emit("get_games");
}

function set_players() {
  socket.emit("get_players");
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





