from threading import Thread
from time import sleep
from serial import Serial
import timeit

class RFID_Reader(object):

    def __init__(self):
        self.serial = Serial()
        self.serial.port = '/dev/serial0'
        self.serial.baudrate = 9600
        self.serial.parity = "N"
        self.serial.bytesize = 8


    def start(self):
        self.serial.open()

    def stop(self):
        self.serial.close()

    def read(self):
        out = ""
        buffer_len = self.serial.inWaiting()
        if buffer_len >= 16:
            out += self.serial.read(buffer_len)
            if out!="":
                return True, out[1:11]
            else:
                return False,'none'
        else:
            return False, "none"

class Chrono(object):
    
    def __init__(self,socketio=None, redis=None, cards=5):

        self.runChrono = False
        self.chronoThread = None
        self.redis = redis
        self.socketio = socketio
        self._card_quantity = cards
        self.RFID_reader = RFID_Reader()
        self._card_ids = []
        self._lapInfo = {'First': None,
                         'LapTime': None
                         }


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
        self.card_ids = []
        self.times = []
        self.chronoThread = Thread(target=self.chronoTask)
        self.runChrono = True
        print 'Starting chrono'
        self.chronoThread.start()
        return True

    def chronoTask(self):
        #TODO: Chrono here
        self.RFID_reader.start()
        while self.runChrono:
            success, response = self.RFID_reader.read()
            if success and len(response)==10:
                print str(response)
                print self._lapInfo
                if response in self._card_ids:
                    if len(self._card_ids)==self._card_quantity and self._card_ids[0]==response:
                        last = timeit.default_timer()
                        self._lapInfo['LapTime'] = last - self._lapInfo['First']
                        print 'LAP DONE'
                        print self._lapInfo
                        if self.socketio is not None:
                            self.socketio.emit('Chrono event',
                                                {'data':str(self._lapInfo['LapTime'])},
                                                broadcast=True)
                        self._lapInfo['First'] = last
                        self._lapInfo['LapTime'] = None
                        self._card_ids = []
                        self._card_ids.append(response)
                    else:
                        print 'Bad done.... Restarting counter'
                        self._lapInfo['First'] = None
                        self._card_ids = []
                        self._lapInfo['First'] = timeit.default_timer()
                        self._card_ids.append(response)
                else:
                    self._card_ids.append(response)
                    print 'New card detected'
                    if self._lapInfo['First'] is None:
                        print 'first card so... Starting chrono'
                        self._lapInfo['First'] = timeit.default_timer()

            sleep(0.1)
        self.RFID_reader.stop()
        self._card_ids = []
        self._lapInfo['First'] = None
        self._lapInfo['LapTime'] = None


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
