from app import dummy
from app.sessionManager.tools import check_permission
from flask import jsonify

@dummy.route("/test")
@check_permission
def test(data):
    print 'Front-end event'
    return jsonify(success=True)
