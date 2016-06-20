
#TODO: - Check last poll for erasing memory ONLY IF NECESARY
#TODO: - Improve logging


from flask import render_template, redirect, url_for, request, g, jsonify, current_app, session, Response
from flask_socketio import disconnect
from functools import wraps

from datetime import datetime, timedelta
from app import app, socketio, zumo, checker, weblab, redisClient, board_manager, chrono
from camera_pi import Camera
from config import basedir, ideIP, blocklyIP, DEBUG

import json
import random
import requests
import os
import time

#TODO: Improve error checking tasks and report critical errors here
@checker.route('/check')
def check():
    error = redisClient.hget('zumo:board','error')
    if error == 'Arduino not responding':
        return 'REBOOT'
    else:
        return 'SUCCESS!!'

##################################
#######------>WEBLAB<-------######
##################################

def check_permission(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session_id = session.get('zumo_session_id')
        if not session_id:
            return jsonify(error=False, auth=False, reason="No zumo_session_id found in cookies")

        user_data = get_user_data(session_id)
        if user_data is None:
            return jsonify(error=False, auth=False, reason="session_id not found in Redis")

        if user_data['exited'] == 'true':
            return jsonify(error=False, auth=False, reason="User had previously clicked on logout")

        user_data['session_id'] = session_id

        renew_poll(session_id)
        g.user = user_data
        return func(*args, **kwargs)

    return wrapper


@zumo.route('/home')
@check_permission
def home():

    chrono.startChrono()
    #Check if users has his code on the IDE
    try:
        print "doing request to "+ ideIP
        resp = requests.get('http://'+ ideIP +'/binary/'+g.user['username'],timeout=10)
        print resp.content
        data= json.loads(resp.content)
        session['ide_folder_id'] =  data["folder"]
        session['ide_sketch'] = data["sketch"]

    except:
        print "Error doing request"
        session['ide_folder_id'] = "None"
        session['ide_sketch'] = "None"

    #Check if users has his code on the IDE
    try:
        print "doing request to "+ blocklyIP
        resp = requests.get('http://'+ blocklyIP +'/binary/'+g.user['username'],timeout=10)
        print resp.content
        data = json.loads(resp.content)
        session['blockly_folder_id'] =  data["folder"]
        session['blockly_sketch'] = data["sketch"]

    except:
        print "Error doing request"
        session['blockly_folder_id'] = "None"
        session['blockly_sketch'] = "None"

    time = int(get_time_left(session['zumo_session_id']))
    demo_files2 = os.listdir(basedir+'/binaries/demo')
    demo_files=[]
    for demo in demo_files2:
        demo_files.append(demo.split(".")[0])
    return render_template('index.html',
                           title='Home',
                           back=g.user['back'],
                           timeleft=time,
                           demo_files=demo_files,
                           debug = DEBUG)


#############################################
### -----------> SocketIO <-----------#######
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


@zumo.route('/sendserial', methods=['POST'])
@check_permission
def sendSerial():
    message =  request.form['content']
    if board_manager.sendSerial(message):
        return jsonify(success=True)
    else:
        return jsonify(success=False)

#############################################
#### ----------> VIDEO <--------------#######
#############################################
def gen(camera):
    """Video streaming generator function."""
    while True:
        try:
            time.sleep(0.3)
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except:
            break



@zumo.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


#############################################
##### ----------> BUTTONS <-----------#######
#############################################

@zumo.route("/buttonon/<button>",methods=['GET'])
@check_permission
def turnOn(button):
    success = board_manager.buttonOn(button)
    return jsonify(success = success)

@zumo.route("/buttonoff/<button>",methods=['GET'])
@check_permission
def turnOff(button):
    success = board_manager.buttonOff(button)
    return jsonify(success = success)



@zumo.route("/loadbinary", methods=['POST'])
@check_permission
def load():

    if get_time_left(session['zumo_session_id']) <= 20:
        print 'Not time enough'
        return jsonify(success=False)

    name = request.form['name']
    demo = request.form['demo'] == "true"
    ide = request.form['ide']

    if not demo:
        if(session['ide_folder_id'] =="None" and session['blockly_folder_id'] =="None"):
            print "No users code"
        else:
            try:
                print "Downloading user code"

                files = os.listdir(basedir+'/binaries/user')
                for f in files:
                    os.remove(basedir+'/binaries/user/'+f)
                if ide == "blockly":
                    filepath =  'http://'+blocklyIP+'/static/binaries/'+ session['blockly_folder_id'] +'/' + session['blockly_sketch'] +'.hex'
                else:
                    filepath = 'http://'+ideIP+'/static/binaries/'+ session['ide_folder_id']+'/'+ session['ide_sketch'] +'.hex'

                response = requests.get(filepath,timeout=10)
                f=open(basedir+'/binaries/user/'+name+'.hex','a')
                f.write(response.content)
                f.close()
            except:
                print 'Error getting user code'
                return jsonify(success=False)
    if(demo):
        path = basedir+'/binaries/demo/'+name+'.hex'
    else:
        path = basedir+'/binaries/user/'+name+'.hex'

    success = board_manager.loadBinary(path)

    return jsonify(success=success)

#############################################
### ------------> WEBLAB <------------#######
#############################################

@zumo.route('/logout')
@check_permission
def logout():
    print g.user['username'] +' going out'
    app.logger.info(g.user['username'] + ' logout')

    force_exited(g.user['session_id'])
    print "User close session and memory is going to be erased"

    chrono.stopChrono()
    board_manager.eraseMemory()
    return jsonify(error=False,auth=False)


@zumo.route('/poll')
@check_permission
def poll():
    print g.user['username'] +' polled'
    app.logger.info(g.user['username'] + ' polled')
    # In JavaScript, use setTimeout() to call this method every 5 seconds or whatever
    # Save in User or Redis or whatever that the user has just polled
    return jsonify(error=False,auth=True)


def get_user_data(session_id):
    pipeline = redisClient.pipeline()
    pipeline.hget("weblab:active:{}".format(session_id), "back")
    pipeline.hget("weblab:active:{}".format(session_id), "last_poll")
    pipeline.hget("weblab:active:{}".format(session_id), "max_date")
    pipeline.hget("weblab:active:{}".format(session_id), "username")
    pipeline.hget("weblab:active:{}".format(session_id), "exited")
    back, last_poll, max_date, username, exited = pipeline.execute()
    if last_poll is None:
        return None

    return {
        'back': back,
        'last_poll': last_poll,
        'max_date': max_date,
        'username': username,
        'exited': exited
    }

def get_last_poll():
    last_poll = datetime.now()
    last_poll_int = last_poll.strftime('%s') + str(last_poll.microsecond / 1e6)[1:]
    return last_poll_int

def renew_poll(session_id):
    last_poll_int = get_last_poll()
    pipeline = redisClient.pipeline()
    pipeline.hget("weblab:active:{}".format(session_id), "max_date")
    pipeline.hset("weblab:active:{}".format(session_id), "last_poll", last_poll_int)
    max_date, _ = pipeline.execute()
    if max_date is None:
        pipeline.delete("weblab:active:{}".format(session_id))

def force_exited(session_id):
    pipeline = redisClient.pipeline()
    pipeline.hget("weblab:active:{}".format(session_id), "max_date")
    pipeline.hset("weblab:active:{}".format(session_id), "exited", "true")
    max_date, _ = pipeline.execute()
    if max_date is None:
        pipeline.delete("weblab:active:{}".format(session_id))

def get_time_left(session_id):
    current_time = datetime.now()
    current_time = float(current_time.strftime('%s') + str(current_time.microsecond / 1e6)[1:])

    max_date = redisClient.hget("weblab:active:{}".format(session_id), "max_date")
    if max_date is None:
        return 0

    return float(max_date) - current_time


#####################################
# 
# Main method. Authorized users
# come here directly, with a secret
# which is their identifier. This
# should be stored in a Redis or 
# SQL database.

@zumo.route("/lab/<session_id>/")
def index(session_id):
    user_data = get_user_data(session_id)
    if user_data is None:
        print 'User is none'
        return "Session identifier not found"

    renew_poll(session_id)
    session['zumo_session_id'] = session_id
    if not DEBUG:
        return redirect(url_for('.home', _external = True,_scheme="https"))
    else:
        return redirect(url_for('.home', _external = True))

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
        print("In theory this is weblab. However, it provided as credentials: {} : {}".format(username, password))
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
    pipeline.hset('weblab:active:{}'.format(session_id), 'max_date', max_date_int)
    pipeline.hset('weblab:active:{}'.format(session_id), 'last_poll', last_poll_int)
    pipeline.hset('weblab:active:{}'.format(session_id), 'username', server_initial_data['request.username'])
    pipeline.hset('weblab:active:{}'.format(session_id), 'back', request_data['back'])
    pipeline.hset('weblab:active:{}'.format(session_id), 'exited', 'false')
    pipeline.expire('weblab:active:{}'.format(session_id), 30 + int(float(server_initial_data['priority.queue.slot.length'])))
    pipeline.execute()
    if not DEBUG:
        link = url_for('zumo.index', session_id=session_id, _external = True, _scheme="https")

    else:
        link = url_for('zumo.index', session_id=session_id, _external = True)
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

    last_poll = redisClient.hget("weblab:active:{}".format(session_id), "last_poll")
    max_date = redisClient.hget("weblab:active:{}".format(session_id), "max_date")
    username = redisClient.hget("weblab:active:{}".format(session_id), "username")
    exited = redisClient.hget("weblab:active:{}".format(session_id), "exited")
    
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
    chrono.stopChrono()
    board_manager.eraseMemory()
    request_data = get_json()
    if 'action' in request_data and request_data['action'] == 'delete':
        back = redisClient.hget("weblab:active:{}".format(session_id), "back")
        if back is not None:
            pipeline = redisClient.pipeline()
            pipeline.delete("weblab:active:{}".format(session_id))
            pipeline.hset("weblab:inactive:{}".format(session_id), "back", back)
            # During half an hour after being created, the user is redirected to
            # the original URL. After that, every record of the user has been deleted
            pipeline.expire("weblab:inactive:{}".format(session_id), 3600)
            pipeline.execute()
            return 'deleted'
        return 'not found'
    return 'unknown op'

