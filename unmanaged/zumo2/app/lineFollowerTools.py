from threading import Thread
from time import sleep

class Chrono(object):
    
    def __init__(self,socketio=None, redis=None):

        self.runChrono = False
        self.chronoThread = None
        self.redis = redis
        self.socketio = socketio
        
    def startChrono(self):
        
        if self.chronoThread is None:
            print 'Thread not running'
        else:
            if self.chronoThread.isAlive():
                print 'Chrono thread running...stop'
                self.runChrono = False
                self.chronoThread.join()
                print 'Chrono thread stopped'
            else:
                print 'Chrono thread is not running'

        self.chronoThread = Thread(target=self.chronoTask)
        self.runChrono = True
        print 'Starting chrono'
        self.chronoThread.start()
        return True

    def chronoTask(self):
        while self.runChrono:
            if self.socketio is not None:
                self.socketio.emit('Chrono event',
                      {'data':'Testing chrono sockets'},
                      broadcast=True)
            sleep(2)


    def stopChrono(self):
        if self.chronoThread is None:
            print 'Chrono not running'
            return False
        if self.chronoThread.isAlive():
            self.runChrono = False
            self.chronoThread.join()
            print 'Chrono stopped'
            return True
        print 'Chrono not running'
        return False