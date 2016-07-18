from flask import jsonify, session, g
from functools import wraps
from datetime import datetime
from app import redisClient

def check_permission(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session_id = session.get('session_id')
        if not session_id:
            return jsonify(error=False, auth=False, reason="No session_id found in cookies")

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

def get_user_data(session_id):
    pipeline = redisClient.pipeline()
    pipeline.hget("sessionManager:active:{}".format(session_id), "back")
    pipeline.hget("sessionManager:active:{}".format(session_id), "last_poll")
    pipeline.hget("sessionManager:active:{}".format(session_id), "max_date")
    pipeline.hget("sessionManager:active:{}".format(session_id), "username")
    pipeline.hget("sessionManager:active:{}".format(session_id), "exited")
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
    pipeline.hget("sessionManager:active:{}".format(session_id), "max_date")
    pipeline.hset("sessionManager:active:{}".format(session_id), "last_poll", last_poll_int)
    max_date, _ = pipeline.execute()
    if max_date is None:
        pipeline.delete("sessionManager:active:{}".format(session_id))

def force_exited(session_id):
    pipeline = redisClient.pipeline()
    pipeline.hget("sessionManager:active:{}".format(session_id), "max_date")
    pipeline.hset("sessionManager:active:{}".format(session_id), "exited", "true")
    max_date, _ = pipeline.execute()
    if max_date is None:
        pipeline.delete("sessionManager:active:{}".format(session_id))

def get_time_left(session_id):
    current_time = datetime.now()
    current_time = float(current_time.strftime('%s') + str(current_time.microsecond / 1e6)[1:])

    max_date = redisClient.hget("sessionManager:active:{}".format(session_id), "max_date")
    if max_date is None:
        return 0

    return float(max_date) - current_time

