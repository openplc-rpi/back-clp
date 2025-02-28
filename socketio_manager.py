from flask_socketio import emit
import json
from random import randint
import threading
import time

from globals import socketio


@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
