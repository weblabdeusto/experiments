import json
import random
from flask import Response, current_app, url_for, request
from app import redisClient, weblab, lab
from datetime import datetime, timedelta
from tools import get_last_poll
from config import DEBUG

def get_json():
    # Retrieve the submitted JSON
    if request.data:
        data = request.data
    else:
        keys = request.form.keys() or ['']
        data = keys[0]
    return json.loads(data)

#############################################################
#
# WebLab-Deusto API:
#
# First, this method creates new sessions. We store the
# sessions on memory in this dummy example.
#
@weblab.before_request
def require_http_credentials():
    auth = request.authorization
    if auth:
        username = auth.username
        password = auth.password
    else:
        username = password = "No credentials"

    weblab_username = current_app.config['WEBLAB_USERNAME']
    weblab_password = current_app.config['WEBLAB_PASSWORD']
    if username != weblab_username or password != weblab_password:
        print("In theory this is sessionManager. However, it provided as credentials: {} : {}".format(username, password))
        return Response(response=("You don't seem to be a WebLab-Instance"), status=401, headers = {'WWW-Authenticate':'Basic realm="Login Required"'})

@weblab.route("/sessions/", methods=['POST'])
def start_experiment():
    # Parse it: it is a JSON file containing two fields:
    request_data = get_json()

    client_initial_data = json.loads(request_data['client_initial_data'])
    server_initial_data = json.loads(request_data['server_initial_data'])

    # Parse the initial date + assigned time to know the maximum time
    start_date_str = server_initial_data['priority.queue.slot.start']
    start_date_str, microseconds = start_date_str.split('.')
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S") + timedelta(microseconds = int(microseconds))
    max_date = start_date + timedelta(seconds = float(server_initial_data['priority.queue.slot.length']))

    # Create a global session
    session_id = str(random.randint(0, 10e8)) # Not especially secure 0:-)

    # Prepare adding this to redis
    max_date_int = max_date.strftime('%s') + str(max_date.microsecond / 1e6)[1:]
    last_poll_int = get_last_poll()

    pipeline = redisClient.pipeline()
    pipeline.hset('sessionManager:active:{}'.format(session_id), 'max_date', max_date_int)
    pipeline.hset('sessionManager:active:{}'.format(session_id), 'last_poll', last_poll_int)
    pipeline.hset('sessionManager:active:{}'.format(session_id), 'username', server_initial_data['request.username'])
    pipeline.hset('sessionManager:active:{}'.format(session_id), 'back', request_data['back'])
    pipeline.hset('sessionManager:active:{}'.format(session_id), 'exited', 'false')
    pipeline.expire('sessionManager:active:{}'.format(session_id), 30 + int(float(server_initial_data['priority.queue.slot.length'])))
    pipeline.execute()
    if not DEBUG:
        link = url_for('lab.index', session_id=session_id, _external = True, _scheme="https")

    else:
        link = url_for('lab.index', session_id=session_id, _external = True)
    print "Assigned session_id: %s" % session_id
    print "See:",link
    return json.dumps({ 'url' : link, 'session_id' : session_id })


#############################################################
#
# WebLab-Deusto API:
#
# This method provides the current status of a particular
# user.
#
@weblab.route('/sessions/<session_id>/status')
def status(session_id):
    print "Weblab status check"

    last_poll = redisClient.hget("sessionManager:active:{}".format(session_id), "last_poll")
    max_date = redisClient.hget("sessionManager:active:{}".format(session_id), "max_date")
    username = redisClient.hget("sessionManager:active:{}".format(session_id), "username")
    exited = redisClient.hget("sessionManager:active:{}".format(session_id), "exited")

    if exited == 'true':
        return json.dumps({'should_finish' : -1})

    if last_poll is not None:
        current_time = datetime.now()
        current_time = float(current_time.strftime('%s') + str(current_time.microsecond / 1e6)[1:])
        difference = current_time - float(last_poll)
        print "Did not poll in", difference, "seconds"
        if difference >= 15:
            return json.dumps({'should_finish' : -1})

        print "User %s still has %s seconds" % (username, (float(max_date) - current_time))

        if float(max_date) <= current_time:
            print "Time expired"
            return json.dumps({'should_finish' : -1})

        return json.dumps({'should_finish' : 5})

    print "User not found"
    #
    # If the user is considered expired here, we can return -1 instead of 10.
    # The WebLab-Deusto scheduler will mark it as finished and will reassign
    # other user.
    #
    return json.dumps({'should_finish' : -1})


#############################################################
#
# WebLab-Deusto API:
#
# This method is called to kick one user out. This may happen
# when an administrator defines so, or when the assigned time
# is over.
#
@weblab.route('/sessions/<session_id>', methods=['POST'])
def dispose_experiment(session_id):
    print "Weblab trying to delete user"
    print "Weblab erasing memory"
    request_data = get_json()
    if 'action' in request_data and request_data['action'] == 'delete':
        back = redisClient.hget("sessionManager:active:{}".format(session_id), "back")
        if back is not None:
            pipeline = redisClient.pipeline()
            pipeline.delete("sessionManager:active:{}".format(session_id))
            pipeline.hset("wetblab:inactive:{}".format(session_id), "back", back)
            # During half an hour after being created, the user is redirected to
            # the original URL. After that, every record of the user has been deleted
            pipeline.expire("sessionManager:inactive:{}".format(session_id), 3600)
            pipeline.execute()
            return 'deleted'
        return 'not found'
    return 'unknown op'

