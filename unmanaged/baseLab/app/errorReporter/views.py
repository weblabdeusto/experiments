from app import redisClient, checker

@checker.route('/check')
def check():
    error = redisClient.hget('dummy:general','error')
    if error == 'Critical error':
        return 'SHUT_DOWN'
    else:
        return 'SUCCESS'