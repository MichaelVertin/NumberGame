import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from game_logic import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret'
socketio = SocketIO(app, async_mode='eventlet')

GLOBAL_GAME = NumberGame("ALICE", "BOB")

@app.route('/')
def index():
    return render_template('index.html')

def get_turn_obj(data):
    try:
        if data["type"] == "draw":
            turn_obj = Turn_Draw(GLOBAL_GAME)
        elif data["type"] == "attack":
            turn_obj = Turn_Attack(GLOBAL_GAME, 
                                   data["cards"])
        else:
            emit('set_selection_status', {"status": "False", "message": "To draw, only select the deck"}) # TODO # implement this into javascript
            return
        return turn_obj
    except SelectionError as e:
        emit('set_selection_status', {"status": "False", "message":str(e)})
        



@socketio.on('update_state')
def update_state():
    state = GLOBAL_GAME.get_state()
    active_player = GLOBAL_GAME.get_active_player()
    score = GLOBAL_GAME.get_score()
    emit('set_state', {"cards": state, 
                       "active_player": active_player, 
                       "score": score})

@socketio.on('check_selection')
def check_selection(data):
    try:
        turn_obj = get_turn_obj(data)
        if not turn_obj: return # TODO: remove
        status = turn_obj.validate()
        emit('set_selection_status', status)
    except SelectionError as e:
        emit('set_selection_status', {"status": "False", "message":str(e)})

@socketio.on('send_move')
def send_move(data):
    try:
        turn_obj = get_turn_obj(data)
        if not turn_obj: return # TODO: remove
        status = turn_obj.execute()
        update_state()
        emit('set_selection_status', status)
    except SelectionError as e:
        emit('set_selection_status', {"status": "False", "message":str(e)})

if __name__ == '__main__':
    print("Running on port 5000")
    socketio.run(app, host='0.0.0.0', port=5000)


