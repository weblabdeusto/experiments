from flask import render_template, g, jsonify, redirect, url_for, session
from sessionManager.tools import force_exited, check_permission
from app import app, lab
from config import APPLICATION_ROOT, DEBUG
from app.sessionManager.tools import get_user_data, renew_poll, get_time_left

@lab.route('/home')
@check_permission
def home():
    time = int(get_time_left(session['session_id']))
    return render_template('index.html',
                           title='Home',
                           back=g.user['back'],
                           timeleft=time,
                           DEBUG = DEBUG,
                           base_url = APPLICATION_ROOT)

@lab.route('/logout')
@check_permission
def logout():
    print g.user['username'] +' going out'
    app.logger.info(g.user['username'] + ' logout')

    force_exited(g.user['session_id'])
    print "User close session and memory is going to be erased"

    return jsonify(error=False,auth=False)

@lab.route('/poll')
@check_permission
def poll():
    print g.user['username'] +' polled'
    app.logger.info(g.user['username'] + ' polled')
    # In JavaScript, use setTimeout() to call this method every 5 seconds or whatever
    # Save in User or Redis or whatever that the user has just polled
    return jsonify(error=False, auth=True)

@lab.route("/lab/<session_id>/")
def index(session_id):
    user_data = get_user_data(session_id)
    if user_data is None:
        print 'User is none'
        return "Session identifier not found"

    renew_poll(session_id)
    session['session_id'] = session_id

    if not DEBUG:
        return redirect(url_for('lab.home', _external = True,_scheme="https"))
    else:
        return redirect(url_for('lab.home', _external = True))

