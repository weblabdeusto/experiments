from flask import render_template, redirect, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, \
    login_required

from datetime import datetime, timedelta
from app import app, db, lm, celery
from config import basedir
from .models import User
from functools import wraps
import json

import random

import os
from uuid import uuid4

import subprocess

@app.route('/test')
def test():
    return 'SUCCESS!!'

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
                return jsonify(error=False, auth=False)
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
#        db.session.add(g.user)
#        db.session.commit()

@app.route('/home')
@login_required
@check_permission
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
    return jsonify(error=False,auth=True)


@app.route('/poll')
@check_permission
@login_required
def poll():
    g.user.last_poll = datetime.now()
    #g.user.last_poll = datetime.now()
    db.session.add(g.user)
    db.session.commit()
    print 'polled'
    # In JavaScript, use setTimeout() to call this method every 5 seconds or whatever
    # Save in User or Redis or whatever that the user has just polled
    return jsonify(error=False,auth=True)

################################
## -------> COMPILER <------- ##
################################

@celery.task(bind=True)
def compile_project(self,user_folder,board):


    self.update_state(state='PROGRESS',
                      meta={'current': 0, 'total': 100,
                            'status': "Preparing files"})

    try:
        result = subprocess.check_output(["sh", basedir+"/app/scripts/build.sh",board, basedir], stderr=subprocess.STDOUT)
        print "Success!"
        self.update_state(state='PROGRESS',
                      meta={'current': 50, 'total': 100,
                            'status': result})
    except subprocess.CalledProcessError, ex: # error code <> 0
        print "--------errors------"
        lines = ex.output.split("\n")
        print len(lines)
        index = 0
        errors = ""
        for line in lines:
            #print line
            if "error" in line:
                errors = errors + line + "%%%" + lines[index+1] + "%%%" + lines[index+2] + "%%%"

                print "\t"+line
                print "\t"+lines[index+1]
                print "\t"+lines[index+2]
            if "main" in line:
                 print "\t"+line
                 errors = errors + line + "%%%"

            index=index+1
        self.update_state(state='FAILURE',
                      meta={'current': 90, 'total': 100,
                            'status': "Compiling files"})
        return {'current': 100, 'total': 100, 'status': 'Error',
            'result': errors}

    self.update_state(state='PROGRESS',
                      meta={'current': 90, 'total': 100,
                            'status': "Preparing files"})
    try:
        result = subprocess.check_output(["sh", basedir+"/app/scripts/moveBinary.sh", board, user_folder,'blocks',basedir], stderr=subprocess.STDOUT)
        print "Success!"
        self.update_state(state='PROGRESS',
                      meta={'current': 95, 'total': 100,
                            'status': result})
    except subprocess.CalledProcessError, ex:
        # error code <> 0
        print "Error moving binary"
        #return {'current': 100, 'total': 100, 'status': 'Error!',
        #    'result': "Error moving binary files"}


    result = "Success!"
    return {'current': 100, 'total': 100, 'status': 'Success',
            'result': result}

@app.route('/compile', methods=['POST'])
#@check_permission
@login_required
def compile():

    file_content = request.form['content']
    file_path = os.path.join(basedir, 'app/workspace/src/blocks.ino')
    print file_path

#    try:
    os.remove(file_path)
    f = open(file_path,"w+")
    f.write(file_content)
    f.close()
    print 'file created'
#    except:
#        return jsonify(success=False,auth=True)

    if not os.path.exists(basedir+'/app/static/binaries/'+g.user.folder_id):
        os.makedirs(basedir+'/app/static/binaries/'+g.user.folder_id)
    task = compile_project.apply_async(args=[g.user.folder_id, "leonardo"])

    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}


@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = compile_project.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']

    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

#################################
### -------> ROBOTS <-------- ###
#################################

@app.route("/binary/<user_name>",methods=['GET'])
def binary(user_name):

    user = User.query.filter_by(nickname=user_name).first()
    if user is None:
        return jsonify(folder="None",sketch="None")
    else:
        user_folder = os.path.join(app.config['BINARY_FOLDER'], user.folder_id)
        files = os.listdir(user_folder)
        if len(files)==0:
            return jsonify(folder="None",sketch=None)
        else:
            return jsonify(folder=user.folder_id, sketch=files[0].split(".")[0])

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
    user.permission=True
    db.session.add(user)
    db.session.commit()
    login_user(user)
    print 'Redirecting user to home'
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
        folder_id = str(uuid4())
        user = User(nickname=server_initial_data['request.username'], max_date=max_date, last_poll= datetime.now(),
                    back=request_data['back'], session_id=session_id, folder_id=folder_id,permission=True)
        print 'Back URL: ' + user.back
    else:
        print 'User exists'
        if user.folder_id is None:
            folder_id = str(uuid4())
            user.folder_id = folder_id
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
#        if (datetime.now() - user.last_poll).seconds >= 40:
        if (datetime.now() - user.last_poll).seconds >= 3:
            return json.dumps({'should_finish' : -1})
        if user.max_date<=datetime.now():
            print "Time expired"
            return json.dumps({'should_finish' : -1})

        print "User %s still has %s seconds" % (user.nickname, (user.max_date - datetime.now()).seconds)
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
            print 'user ' + user.nickname + ' deleted by weblab but permissions not removed'
            #user.permission = False
            #db.session.add(user)
            #db.session.commit()
            return 'deleted'
        return 'not found'
    return 'unknown op'
