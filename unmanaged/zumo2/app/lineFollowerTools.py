from threading import Thread
from time import sleep
from serial import Serial
class RFID_Reader(object):

    def __init__(self):
        self.serial = Serial()
        self.serial.port = '/dev/serial0'
        self.serial.baudrate = 9600
        self.serial.parity = "N"
        self.serial.bytesize = 8
        self.serial.open()

    def read(self):
        out = ""
        buff_len = self.serial.inWaiting()
        if buff_len != 0:
            out += self.serial.read(buff_len)
            if out!="":
                return True, out[1:11]
            else:
                return False,'none'
        else:
            return False, "none"

class Chrono(object):
    
    def __init__(self,socketio=None, redis=None):

        self.runChrono = False
        self.chronoThread = None
        self.redis = redis
        self.socketio = socketio
        self.RFID_reader = RFID_Reader()
        
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
            success, response = self.RFID_reader.read()
            if success:
                print str(response)
                if self.socketio is not None:
                    self.socketio.emit('Chrono event',
                        {'data':str(response)},
                        broadcast=True)
            sleep(0.1)


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