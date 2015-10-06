#!flask/bin/python
from app import app
from gevent.wsgi import WSGIServer

app.run('0.0.0.0',port=8080,debug=True,threaded=True)

#if __name__ == "__main__":
#    WSGIServer(('', 80), app.wsgi_app).serve_forever()
