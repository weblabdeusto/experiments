
from threading import Thread
import time
import requests

class Axis(object):

    def __init__(self, steps_mm, driverGPIOs, endStopsGPIOs, stepDivisor=1.0, angularVelocity=90):
        stepGPIO = driverGPIOs[0]
        directionGPIO = driverGPIOs[1]
        enableGPIO = driverGPIOs[2]
        homeEndStopGPIO = endStopsGPIOs[0]
        finalEndStopGPIO = endStopsGPIOs[1]
        self._steps_mm = steps_mm
        self._stepGPIO = "/sys/class/gpio/gpio" + str(stepGPIO) + "/value"
        self._directionGPIO = "/sys/class/gpio/gpio" + str(directionGPIO) + "/value"
        self._enableGPIO = "/sys/class/gpio/gpio" + str(enableGPIO) + "/value"
        self._homeEndStopGPIO = "/sys/class/gpio/gpio" + str(homeEndStopGPIO) + "/value"
        self._finalEndStopGPIO = "/sys/class/gpio/gpio" + str(finalEndStopGPIO) + "/value"
        self._stepAngle = 1.8 / stepDivisor
        self._angularVelocity = angularVelocity
        self._defaultVelocity = angularVelocity
        self.setVelocity(self._angularVelocity)
        self._disableStepper()
        self._run = False
        self._stopped = True
        self._position = 0

    @property
    def position(self):
        if self._position<0:
            self._position = 0
        return self._position

    def move(self, direction, mm):
        try:
            if direction == 'forward':
                thread = Thread(target=self._moveForward, args=(mm,))
                thread.start()
                print 'thread launched'
                return True,'moving forward'
            elif direction == 'back':
                thread = Thread(target=self._moveBack, args=(mm,))
                thread.start()
                print 'thread launched'
                return True, 'moving back'
            else:
                return False, 'parameter'
        except:
            print 'Error launching thread'
            return False, 'thread'

    def setVelocity(self, newVel):
        self._angularVelocity = newVel
        turnTime = 60.0/self._angularVelocity
        self._stepPeriod = turnTime/(360/self._stepAngle)
        print 'Step period set in '+ str(self._stepPeriod) + 'seconds'

    def stop(self):
        self._run = False
        print 'Stopping motors'
        while self._stopped != True:
            time.sleep(0.0001)
        self._disableStepper()
        self._stopped = True
        print 'Motors stopped'

    def _disableStepper(self):
        f = open(self._enableGPIO,"w")
        f.write('1')
        f.close()

    def _enableStepper(self):
        f = open(self._enableGPIO,"w")
        f.write('0')
        f.close()

    def _moveForward(self,mm):
        dmm=self._steps_mm/10.0
        if not self._stopped:
            print 'motors on... Stopping'
            self.stop()
        remainingSteps = self._steps_mm * mm
        stepCounter = 0
        self._run = True
        self._stopped = False
        f = open(self._directionGPIO,"w")
        f.write('1')
        f.close()
        self._enableStepper()
        s = open(self._stepGPIO,"w")
        e = open(self._finalEndStopGPIO,"r")
        print 'Needed %d steps'%remainingSteps
        while self._run:
            if '1' in e.read():
                print 'End of the rail'
                e.close()
                break
            e.seek(0)
            s.seek(0)
            s.write('1')
            s.seek(0)
            s.write('0')
            if mm != -1:
                remainingSteps -= 1
                stepCounter += 1
                if stepCounter == dmm:
                    stepCounter = 0
                    self._position += 0.1
                if remainingSteps == 0:
                    break
            time.sleep(self._stepPeriod)
        
        self._position += (stepCounter/self._steps_mm)
        self._position = round(self._position,2)
        print self._position
        s.close()
        self._disableStepper()
        self.setVelocity(self._defaultVelocity)
        self._stopped = True
        self._doACK()
        print 'Motors stopped'

    def _moveBack(self,mm):
        dmm=self._steps_mm/10.0
        if not self._stopped:
            print 'motors on... Stopping'
            self.stop()
        remainingSteps = self._steps_mm * mm
        stepCounter = 0
        self._run = True
        self._stopped = False
        f = open(self._directionGPIO,"w")
        f.write('0')
        f.close()
        self._enableStepper()
        s = open(self._stepGPIO,"w")
        e = open(self._homeEndStopGPIO,"r")
        print 'Needed %d steps'%remainingSteps
        while self._run:
            if '1' in e.read():
                self._position = 0.0
                print 'End of the rail'
                e.close()
                break
            e.seek(0)
            s.seek(0)
            s.write('1')
            s.seek(0)
            s.write('0')
            if mm != -1:
                remainingSteps -= 1
                stepCounter += 1
                if stepCounter == dmm:
                    stepCounter = 0
                    self._position -= 0.1
                if remainingSteps == 0:
                    break
            time.sleep(self._stepPeriod)

        self._position -= (stepCounter/self._steps_mm)
        self._position = round(self._position,2)
        print self._position
        s.close()
        self._disableStepper()
        self.setVelocity(self._defaultVelocity)
        self._stopped = True
        self._doACK()
        print 'Motors stopped'

    def _doACK(self):
        try:
            resp = requests.get('http://weblab.deusto.es/labs/flies/movement_done')
            print resp.content
            print 'ACK done'
        except:
            print 'Error doing ACK'
