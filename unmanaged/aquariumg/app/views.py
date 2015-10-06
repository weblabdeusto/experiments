from flask import render_template, flash, redirect, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, \
    login_required
from datetime import datetime, timedelta
from app import app, db, lm, aq
from .forms import LoginForm
from .models import User
from functools import wraps
import json
import random


@app.route('/test')
def test():
    return 'SUCCESS!!'

def check_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

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


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_poll = datetime.now()
        db.session.add(g.user)
        db.session.commit()

@app.route('/home')
@login_required
def home():
    if g.user.max_date > datetime.now():
        time = (g.user.max_date - datetime.now()).seconds
    else:
        time = 0
    return render_template('index.html',
                           title='Home',
                           user=g.user,
                           timeleft=time)

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
    return jsonify(error=False)

@app.route('/feed')
@check_permission
@login_required
def food():
    resp = aq.tryFeed()
    if resp['success']:
        return jsonify(error=False, auth=True)
    return jsonify(error=True, auth=True, seconds=resp['last'])

@app.route('/light')
@check_permission
@login_required
def light():
    success = aq.turnLightOn()
    if success:
        return jsonify(error=False)
    return jsonify(error=True, auth=True)

@app.route('/poll')
@check_permission
@login_required
def poll():
    g.user.last_poll = datetime.now()
    db.session.add(g.user)
    db.session.commit()
    print 'polled'
    resp = aq.status()
    # In JavaScript, use setTimeout() to call this method every 5 seconds or whatever
    # Save in User or Redis or whatever that the user has just polled
    return jsonify(error=False,lightOn= resp['light']['status'],manualOn=resp['light']['manual'],needFood= resp['food']['need'],lastFood=resp['food']['last'])



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
        print 'Back URL: ' + user.back
    else:
        print 'User exists'
        user.session_id = session_id
        user.back = request_data['back']
        user.last_poll= datetime.now()
        user.max_date = max_date
        print 'Back URL: ' + user.back
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
    print "Weblab status check"
    user = User.query.filter_by(session_id=session_id).first()
    if user is not None: 
        print "Did not poll in", (datetime.now() - user.last_poll).seconds, "seconds"
        if (datetime.now() - user.last_poll).seconds >= 40:
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
