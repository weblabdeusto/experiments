
#TODO: - Check last poll for erasing memory
#TODO: - kick user out when time is out for not depending on weblab
#TODO: - Replace os.system by subprocess.check_output
#TODO: - Analize outputs and detect programming errors
#TODO: - Send message to power manager on critical errors
#TODO: - Send programming error to client
#TODO: - Detect session finish on polling and erase robot's flash memory
#TODO: - Improve logging adding rotating file handlers


from flask import render_template, redirect, url_for, request, g, jsonify, Blueprint, current_app, session
from flask_socketio import disconnect

from datetime import datetime, timedelta
from app import app, socketio, zumo
from config import basedir, ideIP, blocklyIP
from .models import User
from functools import wraps
import json
import random
import requests
import os
import time
import subprocess
import serial
import redis
from threading import Thread, Event

serialThread = None
loadThread = None
serialArdu = serial.Serial()
ArduinoErased = False

redis_client = redis.Redis()

checker_blueprint = Blueprint("checker", __name__)

@checker_blueprint.route('/check')
def check():
    return 'SUCCESS!!'

##################################
#######------>WEBLAB<-------######
##################################

@zumo.before_request
def require_session():
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

@zumo.route('/home')
def home():

    #Check if users has his code on the IDE
    try:
        print "doing request to "+ ideIP
        resp = requests.get('http://'+ ideIP +'/binary/'+g.user['username'],timeout=4)
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
        resp = requests.get('http://'+ blocklyIP +'/binary/'+g.user['username'],timeout=4)
        print resp.content
        data = json.loads(resp.content)
        session['blockly_folder_id'] =  data["folder"]
        session['blockly_sketch'] = data["sketch"]

    except:
        print "Error doing request"
        session['blockly_folder_id'] = "None"
        session['blockly_sketch'] = "None"

    time = int(get_time_left())
    demo_files2 = os.listdir(basedir+'/binaries/demo')
    demo_files=[]
    for demo in demo_files2:
        demo_files.append(demo.split(".")[0])
    #app.logger.info(g.user.nickname +'starting experiment')
    return render_template('index.html',
                           title='Home',
                           timeleft=time,
                           demo_files=demo_files)


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

#############################################
### --------> Event thread <----------#######
### Sends Serial and LapCounter events  #####
#############################################

class myThread(Thread):
    def __init__(self, name='TestThread'):
        """ constructor, setting initial variables """
        self._stopevent = Event()
        Thread.__init__(self, name=name)

    def run(self):
        global serialArdu
        global socketio
        count = 0

        """ main control loop """
        print "%s starts" % (self.getName( ),)
        print 'Serial thread launched'
        socketio.emit('Serial event',
          {'data':'ready'},
          broadcast=True)

        print("Opening serial")
        opened = False
        while not opened:
            try:
                serialArdu.port='/dev/ttyACM'+str(count)
                print serialArdu.port
                serialArdu.baudrate=9600
                serialArdu.parity="N"
                serialArdu.bytesize=8

                serialArdu.open()
                if serialArdu.isOpen():
                    opened = True
                    print 'serial opened'
                else:
                    print('CANT OPEN RETRY...')
            except:
                count=count+1
                if count == 5:
                    count = 0
                print('Cant open serial...retry on /dev/ttyACM'+str(count))

        while not self._stopevent.isSet( ):
            try:
                if serialArdu.isOpen():
                    out=""
                    if serialArdu.inWaiting != 0:
                        buff_len = serialArdu.inWaiting()
                        if buff_len:
                            while buff_len > 0:
                                out += serialArdu.read(1)
                                buff_len=buff_len-1
                            if out!="":
                                print "Sending serial data to client"
                                socketio.emit('Serial event',
                                      {'data':out},
                                      broadcast=True)
                        else:
                            time.sleep(0.2)
                    else:
                        time.sleep(0.2)
            except:
                serialArdu.close()
                time.sleep(1)
                opened=False
                while not opened:
                    try:
                        serialArdu.port='/dev/ttyACM'+str(count)
                        print serialArdu.port
                        serialArdu.baudrate=9600
                        serialArdu.parity="N"
                        serialArdu.bytesize=8

                        serialArdu.open()
                        if serialArdu.isOpen():
                            opened = True
                            print 'serial opened after exception'
                        else:
                            print('CANT OPEN RETRY...')
                    except:
                        time.sleep(0.5)
                        print('Cant open serial...retry on /dev/ttyACM'+str(count))
                        count=count+1
                        if count == 5:
                            count = 0
                    if self._stopevent.isSet():
                        self._stopevent.set()
                        break

            self._stopevent.wait(0.5)
        print "%s ends" % (self.getName( ),)
        serialArdu.close()

    def join(self, timeout=None):
        """ Stop the thread and wait for it to end. """
        self._stopevent.set( )
        Thread.join(self, timeout)

#############################################
#### --------> Lap-Manager <-------------####
#############################################



#############################################
### --------> Serial-Manager <-----------####
#############################################
def startSerial():

    global serialThread

    if serialThread is None:
        print 'Thread not running'
    else:
        if serialThread.isAlive():
            print 'serial thread running...stop'
            serialThread.join()
            time.sleep(2)
            print 'Serial thread stopped'
        else:
            print 'serial thread is not running'
    serialThread = myThread()
    serialThread.setDaemon(True)
    serialThread.start()


def stopSerial():

    global serialArdu
    global serialThread

    try:
        if serialThread is None:
            print 'Thread not running...'

        else:
            if serialThread.isAlive():
                print 'serial thread running...stop'
                serialThread.join()
                time.sleep(2)
                print 'Serial thread stopped'
            else:
                print 'Serial thread not running'
                serialThread = None
        return True
    except:
        print 'Error closing serial'
        return False

@zumo.route('/sendserial', methods=['POST'])
def sendSerial():
    global serialThread
    global serialArdu

    message =  request.form['content']

    if serialThread.isAlive():
        if serialArdu.isOpen():
            serialArdu.write(message)
            return jsonify(success=True)
        else:
            print 'Thread alive but serial closed...'
            return jsonify(success=False)
    else:
        print 'Serial thread is not running'
        return jsonify(success=False)


#############################################
##### ----------> BUTTONS <-----------#######
#############################################

@zumo.route("/buttonon/<button>",methods=['GET'])
def turnOn(button):
    try:
        if button == 'A':
            f=open('/sys/class/gpio/gpio16/value','w')
            f.write('0')
            f.close()
        elif button == 'B':
            f=open('/sys/class/gpio/gpio20/value','w')
            f.write('0')
            f.close()
        elif button == 'C':
            f=open('/sys/class/gpio/gpio26/value','w')
            f.write('0')
            f.close()
        else:
            return jsonify(success=False)

        return jsonify(success=True)
    except:
         return jsonify(success=False)

@zumo.route("/buttonoff/<button>",methods=['GET'])
def turnOff(button):
    try:
        if button == 'A':
            f=open('/sys/class/gpio/gpio16/value','w')
            f.write('1')
            f.close()
        elif button == 'B':
            f=open('/sys/class/gpio/gpio20/value','w')
            f.write('1')
            f.close()
        elif button == 'C':
            f=open('/sys/class/gpio/gpio26/value','w')
            f.write('1')
            f.close()
        else:
            return jsonify(success=False)

        return jsonify(success=True)
    except:
         return jsonify(success=False)


#############################################
### --------> BOOTLOADER <------------#######
#############################################

@zumo.route("/eraseflash", methods=['POST'])
def erase():
    global loadThread
    global serialArdu
    global ArduinoErased

    if ArduinoErased:
        print 'Bootloader is aleready running...'
        return jsonify(success=False)

    print 'Enabling bootloader permanently'
    ArduinoErased = True

    stopSerial()

    if loadThread is None:
        loadThread = Thread(target=eraseThread)
        loadThread.start()
    else:
        if loadThread.isAlive():
            print "Loading thread still runing"
            return jsonify(success=False)
        else:
            loadThread = Thread(target=eraseThread)
            loadThread.start()

    return jsonify(success=True)

def eraseThread():
    global serialArdu

    try:
        f = open("/sys/class/gpio/gpio21/value","w")
        f.write("0")
        f.seek(0)
        time.sleep(0.1)
        f.write("1")
        f.seek(0)
        time.sleep(0.1)
        f.write("0")
        f.seek(0)
        time.sleep(0.1)
        f.write("1")
        f.close()
        print "reset done"

    except:
        print "Error enabling bootloader"
        return

    time.sleep(2)
    try:
        #result = subprocess.check_output('avrdude -c avr109 -p atmega32U4 -P /dev/ttyACM0 -e', stderr=subprocess.STDOUT)
        result = os.system('avrdude -c avr109 -p atmega32U4 -P /dev/ttyACM0 -e')
        print "Success!"

    except subprocess.CalledProcessError, ex:
        # error code <> 0
        print "Error erashing memory"



@zumo.route("/loadbinary", methods=['POST'])
def load():
    global loadThread
    global ArduinoErased


    if get_time_left() <= 20:
        print 'Not time enough'
        return jsonify(success=False)

    ArduinoErased = False

    print 'Stop serial'
    stopSerial()
    print 'Serial stopped'

    name = request.form['name']
    demo = request.form['demo']
    print "loading "+ name

    if demo == "false":
        if(session['ide_folder_id'] =="None" and session['blockly_folder_id'] =="None"):
            print "No users code"
        else:
            try:
                files = os.listdir(basedir+'/binaries/user')
                for f in files:
                    os.remove(basedir+'/binaries/user/'+f)
                if name == "blocks":
                    print 'https://'+blocklyIP+'/static/binaries/'+ session['blockly_folder_id'] +'/' + session['blockly_sketch'] +'.hex'
                    response = requests.get('http://'+blocklyIP+'/static/binaries/'+ session['blockly_folder_id'] +'/'+ session['blockly_sketch'] +'.hex',timeout=10)
                else:
                    response = requests.get('http://'+ideIP+'/static/binaries/'+ session['ide_folder_id']+'/'+ session['ide_sketch'] +'.hex',timeout=10)
                f=open(basedir+'/binaries/user/'+name+'.hex','a')
                f.write(response.content)
                f.close()
            except:
                print 'Error getting user code'
                return jsonify(success=False)

    if loadThread is None:
        loadThread = Thread(target=launch_binary, args=(basedir,name,demo=='true',"leonardo",))
        loadThread.daemon = False
        loadThread.start()
    else:
        if loadThread.isAlive():
            print "Loading thread still runing"
            return jsonify(success=False)
        else:
            loadThread = Thread(target=launch_binary, args=(basedir,name,demo=='true',"leonardo",))
            loadThread.start()
    return jsonify(success=True)

def launch_binary(basedir,file_name,demo,board):
    global serialArdu

    print demo
    print file_name

    try:
        f = open("/sys/class/gpio/gpio21/value","w")
        f.write("0")
        f.seek(0)
        time.sleep(0.1)
        f.write("1")
        f.seek(0)
        time.sleep(0.1)
        f.write("0")
        f.seek(0)
        time.sleep(0.1)
        f.write("1")
        f.close()
        print "reset done"
    except:
        print "Error enabling bootloader"
        return
    print 'Loading code'
    time.sleep(2)
    if(demo):
        #try:
            print file_name
            print 'flash:w:'+basedir+'/binaries/demo/'+file_name+'.hex'
            #subprocess.call('avrdude -p atmega32u4 -c avr109 -P /dev/ttyACM0 -U flash:w:'+basedir+'/binaries/demo/'+file_name+'.hex')

            result = os.system('avrdude -p atmega32u4 -c avr109 -P /dev/ttyACM0 -U flash:w:'+basedir+'/binaries/demo/'+file_name+'.hex')
            print "Success!"


        #except subprocess.CalledProcessError, ex:
            # error code <> 0
        #    print "Error loading file"
        #    return {'current': 100, 'total': 100, 'status': 'Task completed!',
        #        'result': "Error loading binary"}
    else:
        try:
            print file_name
            #result = subprocess.check_output(['avrdude','-p','atmega32u4','-c','avr109','-P','/dev/ttyACM0','-U','flash:w:'+basedir+'/binaries/user/'+file_name+'.hex'], stderr=subprocess.STDOUT)
            result = os.system('avrdude -p atmega32u4 -c avr109 -P /dev/ttyACM0 -U flash:w:'+basedir+'/binaries/user/'+file_name+'.hex')
            print "Success!"

        except subprocess.CalledProcessError, ex:
            # error code <> 0
            print "Error loading file"

    print "Starting serial"
    time.sleep(3)
    startSerial()


#############################################
### ------------> WEBLAB <------------#######
#############################################

@zumo.route('/logout')
def logout():
    print g.user['username'] +' going out'
    app.logger.info(g.user['username'] + ' logout')

    force_exited(g.user['session_id'])
    print "User close session and memory is going to be erased"
    erase()
    return jsonify(error=False,auth=True)


@zumo.route('/poll')
@check_permission
def poll():
    g.user.last_poll = datetime.now()
    print 'polled'
    app.logger.info(g.user.nickname + ' polled')
    if(g.user.max_date<=datetime.now()):
        g.user.permission = False
        g.user.session_id = ""
        db.session.add(g.user)
        db.session.commit()
        erase()
        logout_user()
        return jsonify(error=False,auth=False)
    db.session.add(g.user)
    db.session.commit()
    # In JavaScript, use setTimeout() to call this method every 5 seconds or whatever
    # Save in User or Redis or whatever that the user has just polled
    return jsonify(error=False,auth=True)


def get_user_data(session_id):
    pipeline = redis_client.pipeline()
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
    pipeline = redis_client.pipeline()
    pipeline.hget("weblab:active:{}".format(session_id), "max_date")
    pipeline.hset("weblab:active:{}".format(session_id), "last_poll", last_poll_int)
    max_date, _ = pipeline.execute()
    if max_date is None:
        pipeline.delete("weblab:active:{}".format(session_id))

def force_exited(session_id):
    pipeline = redis_client.pipeline()
    pipeline.hget("weblab:active:{}".format(session_id), "max_date")
    pipeline.hset("weblab:active:{}".format(session_id), "exited", "true")
    max_date, _ = pipeline.execute()
    if max_date is None:
        pipeline.delete("weblab:active:{}".format(session_id))

def get_time_left(session_id):
    current_time = datetime.now()
    current_time = float(current_time.strftime('%s') + str(current_time.microsecond / 1e6)[1:])

    max_date = redis_client.hget("weblab:active:{}".format(session_id), "max_date")
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
    user_data = get_user_data()
    if user_data is None:
        print 'User is none'
        return "Session identifier not found"

    renew_poll(session_id)
    session['zumo_session_id'] = session_id
    return redirect(url_for('.home'))

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

weblab = Blueprint("weblab", __name__)

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

@weblab.route("/weblab/sessions/", methods=['POST'])
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
    
    pipeline = redis_client.pipeline()
    pipeline.hset('weblab:active:{}'.format(session_id), 'max_date', max_date_int)
    pipeline.hset('weblab:active:{}'.format(session_id), 'last_poll', last_poll_int)
    pipeline.hset('weblab:active:{}'.format(session_id), 'username', server_initial_data['request.username'])
    pipeline.hset('weblab:active:{}'.format(session_id), 'back_url', request_data['back'])
    pipeline.hset('weblab:active:{}'.format(session_id), 'exited', 'false')
    pipeline.expire('weblab:active:{}'.format(session_id), 30 + int(server_initial_data['priority.queue.slot.length']))
    pipeline.execute()

    link = url_for('zumo.index', session_id=session_id, _external = True)
    #app.logger.info("Weblab requesting session for "+  user.nickname +", Assigned session_id: " + session_id)
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
@weblab.route('/weblab/sessions/<session_id>/status')
def status(session_id):
    print "Weblab status check"

    last_poll = redis_client.hget("weblab:active:{}".format(session_id), "last_poll")
    max_date = redis_client.hget("weblab:active:{}".format(session_id), "max_date")
    username = redis_client.hget("weblab:active:{}".format(session_id), "username")
    exited = redis_client.hget("weblab:active:{}".format(session_id), "exited")
    
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
@weblab.route('/weblab/sessions/<session_id>', methods=['POST'])
def dispose_experiment(session_id):
    print "Weblab trying to delete user"
    print "Weblab erasing memory"
    erase()
    request_data = get_json()
    if 'action' in request_data and request_data['action'] == 'delete':
        back = redis_client.hget("weblab:active:{}".format(session_id), "back")
        if back is not None:
            pipeline = redis_client.pipeline()
            pipeline.delete("weblab:active:{}".format(session_id))
            pipeline.hset("weblab:inactive:{}".format(session_id), "back", back)
            # During half an hour after being created, the user is redirected to
            # the original URL. After that, every record of the user has been deleted
            pipeline.expire("weblab:inactive:{}".format(session_id), 3600)
            pipeline.execute()
            return 'deleted'
        return 'not found'
    return 'unknown op'

