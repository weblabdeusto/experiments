import time
import subprocess
import serial
from threading import Thread


class BoardManager(object):

    def __init__(self, socketio = None ,redis = None, board = "leonardo",gpios = None):
        self.board = board
        self.serial  = serial.Serial()
        self.serialRun = False
        self.serialThread = None
        self.socketio = socketio
        self.redis = redis
        self.redis.hset('zumo:board','error','none')
        self.erased = False
        self.avrThread = None
        self.gpios = gpios


    def connectSerial(self):
        opened = False
        while not opened:
            try:
                resp = subprocess.check_output(["ls","/dev"])
                resp = resp.split("\n")
                port = ""
                for dev in resp:
                    if "ttyACM" in dev:
                        port = dev
                if port == "":
                    time.sleep(0.2)
                    continue
                self.serial.port='/dev/' + port
                self.serial.baudrate=9600
                self.serial.parity="N"
                self.serial.bytesize=8
                self.serial.open()
                if self.serial.isOpen():
                    opened = True
                    print 'serial opened on '+ self.serial.port
                else:
                    print 'CANT OPEN RETRY...'
                    time.sleep(0.2)
            except:
                print 'Cant open serial...retry'
                time.sleep(0.2)

    def serialTask(self):

        self.connectSerial()
        while self.serialRun:
            try:
                if self.serial.isOpen():
                    out=""
                    if self.serial.inWaiting != 0:
                        buff_len = self.serial.inWaiting()
                        if buff_len:
                            while buff_len > 0:
                                out += self.serial.read(1)
                                buff_len=buff_len-1
                            if out!="":
                                print "Sending serial data to client"
                                if self.socketio is not None:
                                    self.socketio.emit('Serial event',
                                          {'data':out},
                                          broadcast=True)
                        else:
                            time.sleep(0.2)
                    else:
                        time.sleep(0.2)
            except:
                self.serial.close()
                time.sleep(1)
                print "Error detected...Reconnecting serial"
                self.connectSerial()
        self.serial.close()

    #############################################
    ### --------> Serial-Manager <-----------####
    #############################################
    def startSerial(self):

        if self.serialThread is None:
            print 'Thread not running'
        else:
            if self.serialThread.isAlive():
                print 'serial thread running...stop'
                self.serialRun = False
                self.serialThread.join()
                print 'Serial thread stopped'
            else:
                print 'serial thread is not running'
        self.serialRun = True
        self.serialThread = Thread(target= self.serialTask)
        self.serialThread.setDaemon(True)
        self.serialThread.start()


    def stopSerial(self):

        try:
            if self.serialThread is None:
                print 'Thread not running...'

            else:
                if self.serialThread.isAlive():
                    print 'serial thread running...stop'
                    self.serialRun = False
                    self.serialThread.join()
                    print 'Serial thread stopped'
                else:
                    print 'Serial thread not running'
                    self.serialThread = None
            return True
        except:
            print 'Error closing serial'
            return False

    def sendSerial(self,message):
        if self.serialThread.isAlive():
            if self.serial.isOpen():
                self.serial.write(message)
                return True
            else:
                print 'Thread alive but serial closed...'
                return False
        else:
            print 'Serial thread is not running'
            return False

    def buttonOn(self,button):
        try:
            f=open(self.gpios['buttons'][button],'w')
            f.write('0')
            f.close()
            return True
        except:
            return False

    def buttonOff(self,button):
        try:
            f=open(self.gpios['buttons'][button],'w')
            f.write('1')
            f.close()
            return True
        except:
            return False


    def enableBootloader(self):
        try:
            f = open(self.gpios['reset'],"w")
            f.write("0")
            f.seek(0)
            time.sleep(0.1)
            f.write("1")
            f.seek(0)
            time.sleep(0.1)
            f.write("0")
            f.seek(0)
            time.sleep(0.1)
            f.write("1")
            f.close()
            time.sleep(1)
            print "Bootloader enabled"
            return True
        except:
            print "Error enabling bootloader"
            return False

    def eraseMemory(self):

        if self.erased:
            print 'Bootloader is aleready running...'
            return False, "Bootloader running"

        print 'Enabling bootloader permanently'
        self.erased = True

        success = self.stopSerial()

        if self.avrThread is None:
            self.avrThread = Thread(target=self.eraseTask)
            self.avrThread.start()
        else:
            if self.avrThread.isAlive():
                print "Loading thread still runing"
                return False,"Thread running"
            self.avrThread = Thread(target=self.eraseTask)
            self.avrThread.start()

        return True, "Done"

    def eraseTask(self):
        success = self.enableBootloader()
        try:
            resp = subprocess.check_output(["ls","/dev"])
            resp = resp.split("\n")
            port = ""
            for dev in resp:
                if "ttyACM" in dev:
                    port = dev
            if port != "":
                result = subprocess.check_output(['avrdude', '-c' , 'avr109', '-p', 'atmega32U4', '-P', '/dev/'+port, '-e'], stderr=subprocess.STDOUT)
                self.redis.hset('zumo:board','error','none')
                print result
                self.erased = True
            else:
                print "Device not found"
                #TODO: activate error flag
                self.redis.hset('zumo:board','error','Arduino not responding')

        except subprocess.CalledProcessError, ex:
            # error code <> 0
            print "Error erashing memory"



    def loadBinary(self,path):
        success = self.stopSerial()

        if self.avrThread is None:
            self.avrThread = Thread(target=self.programTask, args=(path,))
            self.avrThread.daemon = False
            self.avrThread.start()
        else:
            if self.avrThread.isAlive():
                print "Loading thread still runing"
                return False, "AVR running"
            else:
                self.avrThread = Thread(target=self.programTask, args=(path,))
                self.avrThread.start()
        return True

    def programTask(self,path):

        success = self.enableBootloader()

        try:
            binary = 'flash:w:'+ path
            resp = subprocess.check_output(["ls","/dev"])
            resp = resp.split("\n")
            port = ""
            for dev in resp:
                if "ttyACM" in dev:
                    port = dev
            if port != "":
                result = subprocess.check_output(['avrdude', '-c' , 'avr109', '-p', 'atmega32U4', '-P', '/dev/'+port, '-U',binary], stderr=subprocess.STDOUT)
                print result
                if self.redis is not None:
                    self.redis.hset('zumo:board','error','none')
                if self.socketio is not None:
                    self.socketio.emit('General',
                              {'data':"Ready"},
                              broadcast=True)
                    print "Starting serial"
                    time.sleep(1)
                    self.erased = False
                    self.startSerial()
            else:
                print "Device not found"
                if self.socketio is not None:
                    self.socketio.emit('General',
                              {'data':"Error"},
                              broadcast=True)
                if self.redis is not None:
                    self.redis.hset('zumo:board','error','Arduino not responding')
                return -1

        except subprocess.CalledProcessError, ex:
            print "Exception loading code"
            self.redis.hset('zumo:board','error','AVR not working')
            self.socketio.emit('General',
                              {'data':"Error"},
                              broadcast=True)
