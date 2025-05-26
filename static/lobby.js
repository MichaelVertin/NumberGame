const socket = io();


async function create_player() {
  const username = document.getElementById("self-name").value;

  const response = await fetch("/set_username", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username: username}),
  });
}

function access_game() {
  const game_name = document.getElementById("game-name").value;
  socket.emit("join_game", {"game_name": game_name});
}

function create_game() {
  const game_name = document.getElementById("game-name").value;
  const opponent_name = document.getElementById("opponent-name").value;

  socket.emit("create_game", {"opponent_name": opponent_name, 
                              "game_name": game_name}); 
}

socket.on("load_game", () => {
  window.location.href = "/game";
});



