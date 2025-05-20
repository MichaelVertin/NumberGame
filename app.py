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
    emit('set_state', GLOBAL_GAME.get_state())

@socketio.on('check_selection')
def check_selection(selected_ids):
    try:
        status = GLOBAL_GAME.check_turn(selected_ids)
        emit('set_selection_status', status)
    except Exception as e:
        emit('set_selection_status', {"status": "False", "message":str(e)})


@socketio.on('send_move')
def send_move(selected_ids):
    try:
        GLOBAL_GAME.submit_turn(selected_ids)
        response = update_state()
        emit('set_selection_status', response)
    except Exception as e:
        emit('set_selection_status', {"status": "False", "message":str(e)})


if __name__ == '__main__':
    print("Running on port 5000")
    socketio.run(app, host='0.0.0.0', port=5000)


