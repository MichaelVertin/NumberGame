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



