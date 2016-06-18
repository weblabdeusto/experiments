#!usr/bin/python

from app import app,socketio

socketio.run(app, "0.0.0.0", port=8000,debug=True)
