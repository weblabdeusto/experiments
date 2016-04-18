from flask import render_template, redirect, url_for, request, g, jsonify, send_from_directory
from flask.ext.login import login_user, logout_user, current_user, \
    login_required
from werkzeug.utils import secure_filename

from datetime import datetime, timedelta
from app import app, db, lm, celery
from config import BASE_URL,CAMERA_URL, CAMERA_ENABLED,basedir
from .models import User
from functools import wraps
import json

import random
from uploader.upload_file import uploadfile
import os
from uuid import uuid4

import simplejson
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
#@check_permission
def home():
    if g.user.max_date > datetime.now():
        time = (g.user.max_date - datetime.now()).seconds
    else:
        time = 0

    return render_template('index.html',
                           title='Home',
                           user=g.user,
                           base_url=BASE_URL,
                           cam_enabled = CAMERA_ENABLED,
                           cam_url=CAMERA_URL,
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
#@check_permission
@login_required
def poll():
    g.user.last_poll = datetime.now()
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

    #user_folder = "3037b2d4-bb35-4ad6-a9c8-daa2f489ae69"
    #board="leonardo"
    self.update_state(state='PROGRESS',
                      meta={'current': 0, 'total': 100,
                            'status': "Preparing files"})
    try:
        result = subprocess.check_output(["sh", basedir+"/app/scripts/prepareFiles.sh", user_folder, basedir], stderr=subprocess.STDOUT)
        print "Success!"
        self.update_state(state='PROGRESS',
                  meta={'current': 0, 'total': 100,
                        'status': result})
    except subprocess.CalledProcessError, ex:
        # error code <> 0
        print "Error moving files"
        return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': "Error preparing files"}

    self.update_state(state='PROGRESS',
                      meta={'current': 30, 'total': 100,
                            'status': "Compiling"})
    try:
        result = subprocess.check_output(["sh", basedir+"/app/scripts/build.sh",board, user_folder, basedir], stderr=subprocess.STDOUT)
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
        return {'current': 100, 'total': 100, 'status': 'Error compiling!!',
            'result': errors}

    self.update_state(state='PROGRESS',
                      meta={'current': 90, 'total': 100,
                            'status': "Preparing files"})
    try:
        name=""
        for file in os.listdir(basedir+"/app/static/uploads/"+user_folder):

            if file.split(".")[1]=="ino":
                name=file.split(".")[0]
                break
        result = subprocess.check_output(["sh", basedir+"/app/scripts/moveBinary.sh", board, user_folder,name,basedir], stderr=subprocess.STDOUT)
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
    return {'current': 100, 'total': 100, 'status': 'Project compiled!',
            'result': result}

@app.route('/compile', methods=['POST'])
#@check_permission
@login_required
def compile():
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



################################
## -----> FILE MANAGER <----- ##
################################

def allowed_file(filename):

    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def gen_file_name(folderid,filename):
    """
    If file was exist already, rename it and return a new name
    """

    file_path = os.path.join(folderid, filename)
    print file_path

    if os.path.exists(file_path):
        os.remove(file_path)
        repited = True
    else:
        repited = False

    return filename,repited



@app.route("/upload", methods=['GET', 'POST'])
@check_permission
@login_required
def upload():

    if request.method == 'POST':
        file = request.files['file']
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], g.user.folder_id)
        user_bin_folder =  os.path.join(app.config['BINARY_FOLDER'], g.user.folder_id)

        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        if not os.path.exists(user_bin_folder):
            os.makedirs(user_bin_folder)

        if file:
            filename = secure_filename(file.filename)
            filename,repited = gen_file_name(user_folder, filename)
            print filename
            print repited

            mimetype = file.content_type

            if not allowed_file(file.filename):
                result = uploadfile(name=filename, type=mimetype, size=0, not_allowed_msg="Filetype not allowed")

            else:
                # save file to disk
                uploaded_file_path = os.path.join(user_folder, filename)
                file.save(uploaded_file_path)

                # get file size after saving
                size = os.path.getsize(uploaded_file_path)

                # return json for js call back
                result = uploadfile(name=filename, type=mimetype, size=size)
            if repited:
                return simplejson.dumps({})
            else:
                return simplejson.dumps({"files": [result.get_file()]})

    if request.method == 'GET':
        # get all file in ./data directory
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], g.user.folder_id)
        files = [ f for f in os.listdir(user_folder) if os.path.isfile(os.path.join(user_folder,f)) and f not in app.config['IGNORED_FILES'] ]

        file_display = []

        for f in files:
            size = os.path.getsize(os.path.join(user_folder, f))
            file_saved = uploadfile(name=f, size=size)
            file_display.append(file_saved.get_file())

        return simplejson.dumps({"files": file_display})

    return redirect(url_for('home'))

@app.route("/newfile/<string:filename>", methods=['GET'])
@check_permission
@login_required
def add(filename):
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], g.user.folder_id)
    if not os.path.exists(user_folder):
            os.makedirs(user_folder)
    file_path = os.path.join(user_folder, filename)
    print file_path
    if not os.path.exists(file_path):
        open(file_path, 'a')
        return jsonify(error=False, auth=True)
    else:
        return jsonify(error=True, auth=True)


@app.route("/delete/<string:filename>", methods=['DELETE'])
@check_permission
@login_required
def delete(filename):
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], g.user.folder_id)
    file_path = os.path.join(user_folder, filename)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)


            return simplejson.dumps({filename: 'True'})
        except:
            return simplejson.dumps({filename: 'False'})


@app.route("/data/<string:filename>", methods=['GET'])
@check_permission
@login_required
def get_file(filename):
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], g.user.folder_id)
    return send_from_directory(os.path.join(user_folder), filename=filename)

@app.route("/content/<string:filename>", methods=['GET'])
@check_permission
@login_required
def get_content(filename):

    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], g.user.folder_id)
    file_path = os.path.join(user_folder, filename)

    if os.path.exists(file_path):
        try:
            f = open(file_path,"r")
            cont = f.read()
            f.close()
            print cont
            return jsonify(name=filename,content=cont)
        except:
            return jsonify(name="error",content="")
    return jsonify(name="error",content="Doesnt exist")


@app.route("/save/<filename>",methods=['POST'])
@check_permission
@login_required
def save(filename):
    file_content = request.form['content']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], g.user.folder_id)
    file_path = os.path.join(user_folder, filename)
    print file_path
    try:
        os.remove(file_path)
        f = open(file_path,"a")
        f.write(file_content)
        f.close()
    except:
        return jsonify(success=False,auth=True)

    return jsonify(success=True,auth=True)

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
        if (datetime.now() - user.last_poll).seconds >= 40:
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
            print 'user ' + user.nickname + ' deleted'
            #user.permission = False
            #db.session.add(user)
            #db.session.commit()
            return 'deleted'
        return 'not found'
    return 'unknown op'
