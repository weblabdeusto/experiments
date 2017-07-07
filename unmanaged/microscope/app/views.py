from flask import render_template, redirect, url_for, request, g, jsonify, Response
from flask.ext.login import login_user, logout_user, current_user, \
    login_required
from datetime import datetime, timedelta
from app import app, db, lm
from .models import User, Sample
from config import DEBUG
from functools import wraps
import json
import random
import requests
import time
from camera import Camera
import redis

def check_permission(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            if not g.user.permission:
                g.user.session_id = ""
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


@app.before_request
def before_request():
    g.user = current_user
#    if g.user.is_authenticated:
#        g.user.last_poll = datetime.now()
#        db.session.add(g.user)
#        db.session.commit()

def gen(camera):
    """Video streaming generator function."""
    while True:
        try:
            time.sleep(0.1)
            frame = camera.get_frame()
            print "Frame: "
            print frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except:
            break

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
def events():
        first = True
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = redis.StrictRedis(host='localhost', port=6379, db=13)
        r.set('events:position', 'False')
        while True:
            try:
                time.sleep(0.2)
                while r.get('events:position') != 'True' and not first:

                    time.sleep(0.2)

                if DEBUG != True:
                    resp = requests.get('http://192.168.0.193:8083/position', headers=headers)
                else:
                    resp = requests.get('http://localhost:8083/position', headers=headers)
                x = json.loads(resp.content).get('x','')
                y = json.loads(resp.content).get('y','')
                z = json.loads(resp.content).get('z','')
                des = json.loads(resp.content).get('desired','')
                r.set('events:desiredposition', des)
                r.set('events:position', 'False')
                first = False
                yield "data:%.1f:%.1f:%.1f:%s\n\n" % (round(x,1),round(y,1),round(z,1),str(des))
            except:
                print "position_stream failed"
                break

@app.route('/position_stream')
def stream():
    return Response(events(), content_type='text/event-stream')




@app.route('/push_position')
def pushPosition():
    try:
        r = redis.StrictRedis(host='localhost', port=6379, db=13)
        r.set('events:position', 'True')
        return jsonify(success=True)
    except:
        return jsonify(success=False)

@app.route('/home')
@login_required
def home():
    if datetime.now() >= g.user.max_date:
        time = 0
    else:
        time=(g.user.max_date - datetime.now()).seconds
#    if DEBUG!=True:
#        resp = requests.get("http://192.168.0.193:8083/autohome")
#    else:
#        resp = requests.get("http://localhost:8083/autohome")

    samples=Sample.query.all()
    for s in samples:
        if s.active:
            current = s.id-1
            break

    return render_template('index.html',
                           title='Home',
                           user=g.user,
                           timeleft=time,
                           samples=samples,
                           current=current
                           )

@app.route('/test')
def test():
    return 'WORKS!'

@app.route('/info')
@login_required
def info():
    time=(g.user.max_date - datetime.now()).seconds

#    return render_template('info.html',
#                           title='Info',
#                           timeleft=time)
    return 'infoo'

@app.route('/move', methods=['POST'])
@login_required
@check_permission
def move():
    axis = request.form['axis'].strip()
    direction = request.form['direction'].strip()
    mm = request.form['dist'].strip()

    current_sample = request.form['current_sample'].strip()

    try:
        sample = Sample.query.get(int(current_sample)+1)
        if axis == 'x':
            min = sample.min_x
            max = sample.max_x
        elif axis == 'y':
            min = sample.min_y
            max = sample.max_y
        else:
            min = sample.sample_height
            max = -1
    except:
        print 'error accessing database'
        min = -1
        max = -1

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    data = {'direction': direction,'dist': mm, 'axis': axis, 'min': min, 'max': max}
    data = json.dumps(data)
    r = redis.StrictRedis(host='localhost', port=6379, db=13)
    try:
        if r.get('events:desiredposition')!='False':
            if DEBUG!=True:
                resp = requests.post('http://192.168.0.193:8083/move', data=data, headers=headers)
            else:
                resp = requests.post('http://localhost:8083/move', data=data, headers=headers)
        else:
            print "In movement"
            return jsonify(success=False,auth=True)
        return jsonify(success=True, auth=True)
    except:
        return jsonify(success=False, auth=True)


@app.route('/moveall', methods=['POST'])
@login_required
@check_permission
def moveall():
    x = request.form['x'].strip()
    y = request.form['y'].strip()
    z = request.form['z'].strip()

    current_sample = request.form['current_sample'].strip()
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = redis.StrictRedis(host='localhost', port=6379, db=13)
    if int(current_sample) !=-1:
        sample = Sample.query.get(int(current_sample)+1)
        data = {'x': x,'y': y, 'z': z,'max_x': sample.max_x,'min_x':sample.min_x, 'min_y':sample.min_y, 'max_y':sample.max_y, 'min_z':sample.sample_height, 'max_z': -1}
    else:
        data = {'x': x,'y': y, 'z': z,'max_x': -1,'min_x':-1, 'min_y':-1, 'max_y':-1, 'min_z':-1, 'max_z': -1}
    data = json.dumps(data)
    try:
        print "moveall in position: "+ r.get('events:desiredposition')
        if r.get('events:desiredposition')!='False':
            if DEBUG!= True:
                resp = requests.post('http://192.168.0.193:8083/moveall', data=data, headers=headers)
            else:
                resp = requests.post('http://localhost:8083/moveall', data=data, headers=headers)
            print resp.content
        else:
            print 'in movement'
            return jsonify(success=False,auth=True)
        return jsonify(success=True, auth=True)
    except:
        return jsonify(success=False, auth=True)

@app.route('/stop_all')
@login_required
@check_permission
def stopAll():
    try:
        if DEBUG != True:
            resp = requests.get('http://192.168.0.193:8083/stopall')
        else:
            resp = requests.get('http://localhost:8083/stopall')
        print resp.content
        return jsonify(success=True, auth=True)
    except:
        return jsonify(success=False, auth=True)

@app.route('/movement_done')
def movementDone():
    try:
        print 'movement finished'
        r = redis.StrictRedis(host='localhost', port=6379, db=13)
        r.set('events:movement','True')
        return jsonify(success=True)
    except:
        print 'Error pushing movement finish'
        return jsonify(success=False)

@app.route('/photo')
@login_required
@check_permission
def photo():
    try:
        r = redis.StrictRedis(host='localhost', port=6379, db=13)
        r.set('events:photo','True')
        while r.get('events:photo') == 'True':
            time.sleep(0.1)
        return jsonify(success=True, auth=True)
    except:
        return jsonify(success=False, auth=True)

@app.route('/full_photo')
@login_required
@check_permission
def fullphoto():
    try:
        return jsonify(success=True, auth=True)
    except:
        return jsonify(success=False, auth=True)

def generate_photo():
    print 'doing photo'    

@app.route('/position')
@login_required
@check_permission
def position():
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    try:
        if DEBUG != True:
            resp = requests.get('http://192.168.0.193:8083/position', headers=headers)
        else:
            resp = requests.get('http://localhost:8083/position', headers=headers)
        print resp.content
        x = json.loads(resp.content).get('x','')
        y = json.loads(resp.content).get('y','')
        z = json.loads(resp.content).get('z','')
        return jsonify(success=True, auth=True, x=x, y=y, z=z)
    except:
        return jsonify(success=False, auth=True)

@app.route('/autohome')
@login_required
@check_permission
def autohome():
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    try:
        if DEBUG!=True:
            resp = requests.get('http://192.168.0.193:8083/autohome', headers=headers)
        else:
            resp = requests.get('http://localhost:8083/autohome', headers=headers)
        return jsonify(success=True, auth=True)
    except:
        return jsonify(success=False, auth=True)

@app.route('/updateconf',  methods=['POST'])
@login_required
@check_permission
def updateConfiguration():
    f = request.form
    try:
        for i in range(1,7):

            sample = Sample.query.get(i)
            print sample.id
            sample.active = (f["sample"+str(i)+"[enabled]"]=="true")
            sample.sample_height = float(f["sample"+str(i)+"[height]"])
            print "Sample " + str(i)+": "+str(sample.active)+", "+str(sample.sample_height)
            db.session.add(sample)
            db.session.commit()

        return jsonify(success=True, auth=True)
    except:
        print "Error saving config changes"
        return jsonify(success=False, auth=True)

@app.route('/poll')
@login_required
@check_permission
def poll():
    g.user.last_poll = datetime.now()
    db.session.add(g.user)
    db.session.commit()
    # In JavaScript, use setTimeout() to call this method every 5 seconds or whatever
    # Save in User or Redis or whatever that the user has just polled
    return jsonify(error=False, auth=True)

@app.route('/logout')
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
    return redirect(back)

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

@app.route("/lab/<session_id>/")
def index(session_id):
    user = User.query.filter_by(session_id=session_id).first()
    if user is None:
        return "Session identifier not found"
    user.last_poll = datetime.now()
    user.weblab=True
    user.permission=True
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(url_for('home'))

def get_json():
    # Retrieve the submitted JSON
    if request.data:
        data = request.data
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

@app.route("/weblab/sessions/", methods=['POST'])
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
        print user.back
    else:
        print 'User exists'
        user.session_id = session_id
        user.back = request_data['back']
        user.last_poll= datetime.now()
        user.max_date = max_date
        print user.back
    db.session.add(user)
    db.session.commit()
    link = url_for('index', session_id=session_id, _external = True)
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

@app.route('/weblab/sessions/<session_id>/status')
def status(session_id):
    user = User.query.filter_by(session_id=session_id).first()
    if user is not None: 
        print "Did not poll in", (datetime.now() - user.last_poll).seconds, "seconds"
        if (datetime.now() - user.last_poll).seconds >= 20:
            return json.dumps({'should_finish' : -1})
        print "User %s still has %s seconds" % (user.nickname, (user.max_date - datetime.now()).seconds)
        time = (user.max_date - datetime.now()).seconds
        if  user.max_date <= datetime.now():
            return json.dumps({'should_finish' : -1})
        return json.dumps({'should_finish' : 5})
    #    print "User %s still has %s seconds" % (user.nickname, user.max_date.seconds - datetime.now().seconds)
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

@app.route('/weblab/sessions/<session_id>', methods=['POST'])
def dispose_experiment(session_id):
    request_data = get_json()
    if 'action' in request_data and request_data['action'] == 'delete':
        user=User.query.filter_by(session_id=session_id).first()
        if user is not None:
            user.permission = False
            db.session.add(user)
            db.session.commit()
            return 'deleted'
        return 'not found'
    return 'unknown op'
