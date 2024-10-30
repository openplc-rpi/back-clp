from globals import app, socketio
from flask_socketio import emit
import json

# App Rests
import RestProjects
import RestIoPorts

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('run')
def handle_run_event(data):
    print('Run event received:', data)
    json_data = {"vi1": 0, 
                 "vi2": 1}
    emit('json_data', json.loads(json_data))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)