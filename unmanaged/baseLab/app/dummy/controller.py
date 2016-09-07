from threading import Thread
from time import sleep

class DummyController(object):
    def __init__(self, socketio, redis):
        print 'Dummy controller started'
        ##Initialitation here
        self.runThread = False
        self.Thread = None
        self.redisClient = redis
        self.socketio = socketio

        self.startExperiment()

    #Method definition here
    def startExperiment(self):
        #launch init tasks here
        if self.Thread is None:
                print 'Thread not running'
        else:
            if self.Thread.isAlive():
                print 'Controller thread running...stop'
                self.runThread = False
                self.Thread.join()
                print 'Controller thread stopped'
            else:
                print 'Controller thread is not running'

        self.Thread = Thread(target=self.fakeEventGenerator)
        self.Thread.setDaemon(True)
        self.runThread = True
        print 'Starting experiment'
        self.Thread.start()
        return True

    def stopExperiment(self):
        if self.Thread is None:
            print 'Thread not running'
            return False
        if self.Thread.isAlive():
            self.runThread = False
            self.Thread.join()
            print 'Experiment stopped'
            return True
        print 'Thread not running'
        return False

    def fakeEventGenerator(self):
        while self.runThread:
            if self.socketio is not None:
                self.socketio.emit('Controller event',
                                    {'data':'Controller event'},
                                    broadcast=True)
            sleep(5)


    def doSomething(self):
        self.socketio.emit('Controller event',
                           {'data':'Task started'},
                           broadcast=True)
        sleep(5)
        self.socketio.emit('Controller event',
                           {'data':'Task finished'},
                           broadcast=True)