from flask import render_template, redirect, url_for, request, g, jsonify,session, Blueprint
from flask.ext.login import login_user, logout_user, current_user, \
    login_required
from flask_socketio import  emit, join_room, leave_room, \
    close_room, disconnect

from datetime import datetime, timedelta
from app import app, db, lm, socketio,zumo
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


try:
    serialArdu = serial.Serial()
except:
    print 'Zumo is not connected'

@zumo.route('/test')
def test():
    return 'SUCCESS!!'

##################################
#####------->BACK<----------######
##################################
def background_thread():

    """Example of how to send server generated events to clients."""
    global serialArdu
    count = 0
    run=True
    print 'Thread launched'
    try:
        while run:
            count += 1
            if serialArdu!=None:
                try:
                    #print 'trying...'
                    if serialArdu.isOpen():
                        #print 'Serial waiting for data'
                        out=""
                        if serialArdu.inWaiting()>0:
                            print('Serial data....Reading')
                            while serialArdu.inWaiting() > 0:
                                out += serialArdu.read(1)
                            for line in out.split('\r\n'):
                                if line != "":
                                    socketio.emit('Serial data',
                                          {'data':line, 'count': count},
                                          room= 'Serial',
                                          namespace='/zumo_backend')
                        time.sleep(0.1)
                    else:
                        time.sleep(0.5)
                except:
                    serialArdu.close()
                    print 'Port changed...Wait...'
                    time.sleep(0.5)

            else:
                print 'Waiting for init serial'
                time.sleep(0.5)
    except:
        run = False
        print 'Something unusual happend.....'
        time.sleep(1)


##################################
#######------>WEBLAB<-------######
##################################

def check_permission(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            if not g.user.permission:
                g.user.session_id = ""
                url = g.user.back
                db.session.add(g.user)
                db.session.commit()
                print 'non Authorized'
                logout_user()
                return jsonify(error=True, auth=False)
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
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_poll = datetime.now()
        db.session.add(g.user)
        db.session.commit()

@zumo.route('/home')
#@check_permission
@login_required
def home():
    global serialThread
    global serialArdu

    if serialArdu.isOpen():
        serialArdu.close()
    if serialArdu.isOpen():
        print 'Serial not closed'

    if serialThread is None:
        serialThread = Thread(target=background_thread)
        serialThread.daemon = False
        serialThread.start()

    if g.user.max_date > datetime.now():
        time = (g.user.max_date - datetime.now()).seconds
    else:
        time = 0
    demo_files2 = os.listdir(basedir+'/binaries/demo')
    demo_files=[]
    for demo in demo_files2:
        demo_files.append(demo.split(".")[0])

    return render_template('index.html',
                           title='Home',
                           user=g.user,
                           timeleft=time,
                           demo_files=demo_files)

#############################################
### --------> SERIAL-SOCKET <---------#######
#############################################



@socketio.on('disconnect request', namespace='/zumo_backend')
def disconnect_request():

    global serialArdu

    #TODO:CLose serial
    if serialArdu.isOpen():
        serialArdu.close()

    session['receive_count'] = session.get('receive_count', 0) + 1
    leave_room('Serial')
    close_room('Serial')
    emit('General',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/zumo_backend')
def test_connect():
    print 'Conected to general channel'
    emit('General', {'data': 'Connected', 'count': 0})


@socketio.on('Serial event', namespace='/zumo_backend')
def send_room_message(message):
    global serialArdu
    print message['data']

    session['receive_count'] = session.get('receive_count', 0) + 1
    try:
        if serialArdu.isOpen():
            print 'Sending'
            serialArdu.write(message['data'].encode())
    except:
        print "Error sending data"

@socketio.on('hello', namespace='/zumo_backend')
def test_hello():
    print "user send hello"
    join_room('Serial')
    emit('Serial data', {'data': 'respond', 'count': 0},room= 'Serial')


@socketio.on('Serial start', namespace='/zumo_backend')
def test_connect():
    global serialThread
    global serialArdu

    if serialThread is None:
        print 'Thread not running...launching'
        serialThread = Thread(target=background_thread)
        serialThread.daemon = False
        serialThread.start()
    else:
        if serialThread.isAlive():
            print 'serial thread running'
        else:
            print 'serial thread is stoped'
            serialThread = Thread(target=background_thread)
            serialThread.daemon = False
            serialThread.start()

    print("Opening serial")
    count = 0
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
                join_room('Serial')
                #emit('Serial data',
                #     {'data': 'Serial connected', 'count': 1},
                #     room='Serial')
            else:
                print('CANT OPEN RETRY...')
        except:
            count=count+1
            if count == 5:
                count = 0
            print('Cant open serial...retry on /dev/ttyACM'+str(count))
            time.sleep(0.1)



@socketio.on('close', namespace='/zumo_backend')
def closeSerial():
    global serialArdu

    session['receive_count'] = session.get('receive_count', 0) + 1

    serialArdu.close()
    if not serialArdu.isOpen():
        print 'Serial closed'
        #emit('Serial data', {'data': 'Serial is closing.',
        #                     'count': session['receive_count']},
        #     room='Serial')

    close_room('Serial')

@socketio.on('disconnect', namespace='/zumo_backend')
def test_disconnect():
    global serialArdu

    serialArdu.close()
    if serialArdu.isOpen():
        print 'SERIAL NOT CLOSED!!'
    close_room('Serial')
    print 'user desconected and serial closed'
    print('Client disconnected', request.sid)


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
#@login_required
def erase():
    global loadThread

    if loadThread is None:
        loadThread = Thread(target=eraseThread)
        loadThread.daemon = False
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

    time.sleep(1.5)

    try:
        f = open("/sys/class/gpio/gpio21/value","w")
        f.write("0")
        f.seek(0)
        f.write("1")
        f.seek(0)
        time.sleep(0.1)
        f.write("0")
        f.seek(0)
        f.write("1")
        f.close()
        print "reset done"

    except:
        print "Error enabling bootloader"

    time.sleep(1.5)
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
    global socketio
    print demo
    print file_name
    socketio.emit('General', {'data': 'stopSerial'},namespace='/zumo_backend')
    time.sleep(1.5)
    try:
        f = open("/sys/class/gpio/gpio21/value","w")
        f.write("0")
        f.seek(0)
        f.write("1")
        f.seek(0)
        time.sleep(0.1)
        f.write("0")
        f.seek(0)
        f.write("1")
        f.close()
        print "reset done"
    except:
        print "Error enabling bootloader"
    print 'Loading code'
    time.sleep(1)
    if(demo):
        #try:
            file_name
            print 'flash:w:'+basedir+'/binaries/demo/'+file_name+'.hex'
            #subprocess.call('avrdude -p atmega32u4 -c avr109 -P /dev/ttyACM0 -U flash:w:'+basedir+'/binaries/demo/'+file_name+'.hex')
            res = os.system('ls /dev/tty* -all')
            print res
            result = os.system('avrdude -p atmega32u4 -c avr109 -P /dev/ttyACM0 -U flash:w:'+basedir+'/binaries/demo/'+file_name+'.hex')
            print "Success!"
            time.sleep(1.5)
            socketio.emit('General', {'data': 'startSerial'},namespace='/zumo_backend')
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
            time.sleep(1.5)
            socketio.emit('General', {'data': 'startSerial'},namespace='/zumo_backend')

        except subprocess.CalledProcessError, ex:
            # error code <> 0
            print "Error loading file"


#############################################
### ------------> WEBLAB <------------#######
#############################################


@zumo.route('/logout')
@login_required
def logout():
    print g.user.nickname +' going out'
    g.user.session_id = ""
    g.user.permission = False
    back = g.user.back
    db.session.add(g.user)
    db.session.commit()
    print back
    logout_user()
    print 'logout'
    return jsonify(error=False,auth=True)


@zumo.route('/poll')
@check_permission
@login_required
def poll():
    g.user.last_poll = datetime.now()
    db.session.add(g.user)
    db.session.commit()
    print 'polled'
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
        return "Session identifier not found"
    user.last_poll = datetime.now()
    user.permission=True
    db.session.add(user)
    db.session.commit()
    login_user(user)
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

    #Check if users has his code on the IDE
    try:
        print "doing request to "+ ideIP
        resp = requests.get('http://'+ ideIP +'/binary/'+server_initial_data['request.username'],timeout=4)
        print resp.content
        data= json.loads(resp.content)
        ide_folder_id =  data["folder"]
        ide_sketch = data["sketch"]

    except:
        print "Error doing request"
        ide_folder_id = "None"
        ide_sketch = "None"

    #Check if users has his code on the IDE
    try:
        print "doing request to "+ blocklyIP
        resp = requests.get('http://'+ blocklyIP +'/binary/'+server_initial_data['request.username'],timeout=4)
        print resp.content
        data = json.loads(resp.content)
        blockly_folder_id =  data["folder"]
        blockly_sketch = data["sketch"]

    except:
        print "Error doing request"
        blockly_folder_id = "None"
        blockly_sketch = "None"

    if user is None:
        user = User(nickname=server_initial_data['request.username'], max_date=max_date, last_poll= datetime.now(),
                    back=request_data['back'], session_id=session_id, permission=True, ide_folder_id=ide_folder_id,
                    ide_sketch=ide_sketch, blockly_folder_id=blockly_folder_id, blockly_sketch=blockly_sketch)
    else:
        print 'User exists'
        user.session_id = session_id
        user.back = request_data['back']
        user.last_poll= datetime.now()
        user.max_date = max_date
        user.ide_folder_id = ide_folder_id
        user.ide_sketch = ide_sketch
        user.blockly_folder_id = blockly_folder_id
        user.blockly_sketch = blockly_sketch

    db.session.add(user)
    db.session.commit()
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
@zumo.route('/weblab/sessions/<session_id>/status')
def status(session_id):
    print "Weblab status check"
    user = User.query.filter_by(session_id=session_id).first()
    if user is not None: 
        print "Did not poll in", (datetime.now() - user.last_poll).seconds, "seconds"
        if (datetime.now() - user.last_poll).seconds >= 15:
            return json.dumps({'should_finish' : -1})
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
    erase()
    request_data = get_json()
    if 'action' in request_data and request_data['action'] == 'delete':
        user=User.query.filter_by(session_id=session_id).first()
        print "Weblab trying to delete user"
        if user is not None:
            print user.nickname +" deleted"
            user.permission = False
            db.session.add(user)
            db.session.commit()
        return 'not found'
    return 'unknown op'
