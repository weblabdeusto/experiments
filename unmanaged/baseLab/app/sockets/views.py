from app import socketio
from flask import request
from flask_socketio import disconnect


#############################################
### --------> SocketIO commons <------#######
#############################################

@socketio.on('disconnect request')
def disconnect_request():
    disconnect()

@socketio.on('reconnect')
def test_reconnect():
    print 'Reonected to general channel'
    socketio.emit('General', {'data': 'Reconnected'},broadcast=True)

@socketio.on('connect')
def test_connect():
    print 'Conected to general channel'
    socketio.emit('General', {'data': 'Connected'},broadcast=True)

@socketio.on('disconnect')
def test_disconnect():
    print 'user desconected'
    print('Client disconnected', request.sid)


