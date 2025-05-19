import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('confirm')
def handle_confirm(data):
    print('Received confirmation:', data)
    emit('server_response', {'message': 'Hello from Flask!'}, broadcast=True)

@socketio.on('update_state')
def update_state(data):
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
    emit('set_state', cards)


@socketio.on('check_selection')
def check_selection(selected_ids):
    emit('set_selection_status', {"status": "True", "message": "testing..."});



if __name__ == '__main__':
    print("Running on port 5000")
    socketio.run(app, host='0.0.0.0', port=5000)


