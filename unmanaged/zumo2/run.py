<<<<<<< HEAD
#!/usr/bin/python
=======
#!usr/bin/python
>>>>>>> 11aa72c89dbfda48c983777c050c56531488a88e

from app import app,socketio

socketio.run(app, "0.0.0.0", port=8000,debug=True)
