from app import dummy, socketio, controller
from app.sessionManager.tools import check_permission
from flask import jsonify


@dummy.route("/test")
@check_permission
def test(data):
    print 'Front-end event'
    return jsonify(success=True)

@socketio.on('button')
@check_permission
def button(data):
    print 'Recived: {}'.format(data)
    controller.doSomething()