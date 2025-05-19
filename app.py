import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from game_logic import NumberGame


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')

GLOBAL_GAME = NumberGame("ALICE", "BOB")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('update_state')
def update_state():
    cards = list()
    [cards.append({"owner": "ALICE", "index": index, "value": "---"}) \
        for index in range(10)]
    [cards.append({"owner": "BOB", "index": index, "value": "---"}) \
        for index in range(10)]
    """
    cards = [
        {"owner": "ALICE", "index": 0, "value": "5 / 7"}, 
        {"owner": "BOB", "index": 0, "value": "42 / 24"}, 
        {"owner": "BOB", "index": 1, "value": "123 / 321"}, 
    ]
    """
    # // emit('set_state', cards)
    emit('set_state', GLOBAL_GAME.get_state())

@socketio.on('check_selection')
def check_selection(selected_ids):
    status = GLOBAL_GAME.check_turn(selected_ids)
    emit('set_selection_status', status)
    # emit('set_selection_status', {"status": "True", "message": "testing..."});

@socketio.on('send_move')
def send_move(selected_ids):
    GLOBAL_GAME.submit_turn(selected_ids)
    update_state()

if __name__ == '__main__':
    print("Running on port 5000")
    socketio.run(app, host='0.0.0.0', port=5000)


