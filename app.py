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

if __name__ == '__main__':
    print("Running on port 5000")
    socketio.run(app, host='0.0.0.0', port=5000)


