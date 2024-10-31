import eventlet
eventlet.monkey_patch()

from globals import app, socketio

# App Rests
import RestProjects
import RestIoPorts

import socketio_manager


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)