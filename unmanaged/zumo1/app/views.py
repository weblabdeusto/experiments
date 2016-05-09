from flask import render_template, redirect, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, \
    login_required
from flask_socketio import  emit, join_room, leave_room, \
    close_room, disconnect

from datetime import datetime, timedelta
from app import app, db, lm, socketio, zumo
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
from threading import Thread

serialThread = None
loadThread = None
serialArdu = serial.Serial()


@zumo.route('/test')
def test():
    return 'SUCCESS!!'


##################################
#######------>WEBLAB<-------######
##################################

def check_permission(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            print current_user
            g.user = current_user
            print g.user
            print g.user.nickname + ' connected'
            if not g.user.permission:
                g.user.session_id = ""
                db.session.add(g.user)
                db.session.commit()
                print 'non Authorized'
                logout_user()
                return jsonify(error=False, auth=False)
            return func(*args, **kwargs)
        except:
            print 'non found'
            return jsonify(error=True, auth=False)
    return wrapper

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@zumo.before_request
def before_request():
    print 'request from '+ current_user
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_poll = datetime.now()
        db.session.add(g.user)
        db.session.commit()

@zumo.route('/home')
@check_permission
@login_required
def home():

    #Check if users has his code on the IDE
    try:
        print "doing request to "+ ideIP
        resp = requests.get('http://'+ ideIP +'/binary/'+g.user.nickname,timeout=4)
        print resp.content
        data= json.loads(resp.content)
        g.user.ide_folder_id =  data["folder"]
        g.user.ide_sketch = data["sketch"]

    except:
        print "Error doing request"
        g.user.ide_folder_id = "None"
        g.user.ide_sketch = "None"

    #Check if users has his code on the IDE
    try:
        print "doing request to "+ blocklyIP
        resp = requests.get('http://'+ blocklyIP +'/binary/'+g.user.nickname,timeout=4)
        print resp.content
        data = json.loads(resp.content)
        g.user.blockly_folder_id =  data["folder"]
        g.user.blockly_sketch = data["sketch"]

    except:
        print "Error doing request"
        g.user.blockly_folder_id = "None"
        g.user.blockly_sketch = "None"
    db.session.add(g.user)
    db.session.commit()
    if g.user.max_date > datetime.now():
        time = (g.user.max_date - datetime.now()).seconds
    else:
        time = 0
    demo_files2 = os.listdir(basedir+'/binaries/demo')
    demo_files=[]
    for demo in demo_files2:
        demo_files.append(demo.split(".")[0])
    #app.logger.info(g.user.nickname +'starting experiment')
    return render_template('index.html',
                           title='Home',
                           user=g.user,
                           timeleft=time,
                           demo_files=demo_files)

#############################################
### --------> SERIAL-SOCKET <---------#######
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


import threading

class myThread(threading.Thread):
    def __init__(self, name='TestThread'):
        """ constructor, setting initial variables """
        self._stopevent = threading.Event( )
        threading.Thread.__init__(self, name=name)

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
                            print 'serial opened'
                        else:
                            print('CANT OPEN RETRY...')
                    except:
                        time.sleep(0.5)
                        count=count+1
                        if count == 5:
                            count = 0
                        print('Cant open serial...retry on /dev/ttyACM'+str(count))
                    if self._stopevent.isSet():
                        self._stopevent.set()
                        break

            self._stopevent.wait(0.5)
        print "%s ends" % (self.getName( ),)
        serialArdu.close()

    def join(self, timeout=None):
        """ Stop the thread and wait for it to end. """
        self._stopevent.set( )
        threading.Thread.join(self, timeout)

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
@login_required
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


#############################3################
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
#@login_required
def erase():
    global loadThread
    global serialArdu

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
@login_required
def load():
    global loadThread

    print 'Stop serial'
    stopSerial()
    print 'Serial stopped'

    name = request.form['name']
    demo = request.form['demo']
    print "loading "+ name

    if demo == "false":
        if(g.user.ide_folder_id=="None" and g.user.blockly_folder_id=="None"):
            print "No users code"
        else:
            try:
                files = os.listdir(basedir+'/binaries/user')
                for f in files:
                    os.remove(basedir+'/binaries/user/'+f)
                if name == "blocks":
                    print 'https://'+blocklyIP+'/static/binaries/'+g.user.blockly_folder_id+'/'+g.user.blockly_sketch+'.hex'
                    response = requests.get('http://'+blocklyIP+'/static/binaries/'+g.user.blockly_folder_id+'/'+g.user.blockly_sketch+'.hex',timeout=10)
                else:
                    response = requests.get('http://'+ideIP+'/static/binaries/'+g.user.ide_folder_id+'/'+g.user.ide_sketch+'.hex',timeout=10)
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
            res = os.system('ls /dev/tty* -all')
            print res
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
@login_required
def logout():

    print g.user.nickname +' going out'
    app.logger.info(g.user.nickname + ' logout')
    g.user.session_id = ""
    g.user.permission = False
    back = g.user.back
    db.session.add(g.user)
    db.session.commit()
    logout_user()
    return jsonify(error=False,auth=True)


@zumo.route('/poll')
@login_required
@check_permission

def poll():
    global serialThread

    g.user.last_poll = datetime.now()
    db.session.add(g.user)
    db.session.commit()
    print 'polled'
    app.logger.info(g.user.nickname + ' polled')
    # In JavaScript, use setTimeout() to call this method every 5 seconds or whatever
    # Save in User or Redis or whatever that the user has just polled
    return jsonify(error=False,auth=True)



#################################
### ----->    WEBLAB    <-----###
#################################

#####################################
# 
# Main method. Authorized users
# come here directly, with a secret
# which is their identifier. This
# should be stored in a Redis or 
# SQL database.

@zumo.route("/lab/<session_id>/")
def index(session_id):
    user = User.query.filter_by(session_id=session_id).first()
    if user is None:
        #app.logger.info('%s session id not found' % session_id)
        return "Session identifier not found"
    user.last_poll = datetime.now()
    user.permission=True
    db.session.add(user)
    db.session.commit()
    print 'Login '+ current_user
    login_user(user)

    #app.logger.info('Redirecting %s to the experiment' % user.nickname)
    return redirect(url_for('zumo.home'))

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

@zumo.route("/weblab/sessions/", methods=['POST'])
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
    user=User.query.filter_by(nickname=server_initial_data['request.username']).first()

    if user is None:
        user = User(nickname=server_initial_data['request.username'], max_date=max_date, last_poll= datetime.now(),
                    back=request_data['back'], session_id=session_id, permission=True)
    else:
        print 'User exists'
        user.session_id = session_id
        user.back = request_data['back']
        user.last_poll= datetime.now()
        user.max_date = max_date
        user.permission = True


    db.session.add(user)
    db.session.commit()
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
@zumo.route('/weblab/sessions/<session_id>/status')
def status(session_id):
    print "Weblab status check"
    user = User.query.filter_by(session_id=session_id).first()
    if user is not None: 
        print "Did not poll in", (datetime.now() - user.last_poll).seconds, "seconds"
        if (datetime.now() - user.last_poll).seconds >= 15:
            # app.logger.info(user.nickname + " did not poll in", (datetime.now() - user.last_poll).seconds, "seconds")
            return json.dumps({'should_finish' : -1})
        #app.logger.info( "User %s still has %s seconds" % (user.nickname, (user.max_date - datetime.now()).seconds))
        print "User %s still has %s seconds" % (user.nickname, (user.max_date - datetime.now()).seconds)
        if user.max_date<=datetime.now():
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
@zumo.route('/weblab/sessions/<session_id>', methods=['POST'])
def dispose_experiment(session_id):

    #app.logger.info('Weblab trying to kick user')
    print "Weblab trying to delete user"
    erase()
    request_data = get_json()
    if 'action' in request_data and request_data['action'] == 'delete':
        user=User.query.filter_by(session_id=session_id).first()
        if user is not None:
            print user.nickname +" deleted"
            user.permission = False
            db.session.add(user)
            db.session.commit()
            #app.logger.info( user.nickname +' deleted')
            return 'deleted'
        #app.logger.info( 'User not found')
        return 'not found'
    return 'unknown op'
