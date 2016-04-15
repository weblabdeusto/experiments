from app import app,socketio


socketio.run(app, '0.0.0.0', debug=True)