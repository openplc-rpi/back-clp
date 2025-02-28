from globals import socketio
from flask_socketio import emit
import json
from random import randint
import threading
import time
thread = None
thread_lock = threading.Lock()

def generate_random_json():
    return {
        "Vi1": randint(0, 100),
        "Vi2": randint(0, 100),
        "Ii": randint(0, 100),
        "Di": randint(0, 100),
        "RPI0": randint(0, 100),
        "RPI1": randint(0, 100),
        "RPI2": randint(0, 100)
    }

def background_emit():
    while True:
        socketio.emit('json_data', json.dumps(generate_random_json()))
        time.sleep(1)

@socketio.on('connect')
def handle_connect():
    global thread
    print('Client connected')
    with thread_lock:
        if thread is None:
            thread = threading.Thread(target=background_emit)
            thread.daemon = True
            thread.start()

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
