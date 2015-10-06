from parts import Axis
import requests
from threading import Thread
from time import sleep
import json

class Microscope(object):

    def __init__(self):
        self.xAxis = Axis(steps_mm=80.0,
                          driverGPIOs=(21, 20, 16),
                          endStopsGPIOs=(26, 19),
                          stepDivisor=16.0,
                          angularVelocity=15
                          )
        self.yAxis = Axis(steps_mm=80.0,
                          driverGPIOs=(7, 8, 25),
                          endStopsGPIOs=(13, 6),
                          stepDivisor=16.0,
                          angularVelocity=15
                          )
        self.zAxis = Axis(steps_mm=200.0,
                          driverGPIOs=(18, 15, 14),
                          endStopsGPIOs=(11, 9),
                          stepDivisor=1.0,
                          angularVelocity=150
                          )
        self.autohome()
        self._lastposition = self.position
        self.thread = Thread(target=self.positionUpdater)
        self.thread.start()
        
    @property
    def position(self):

        position = {'x': self.xAxis.position,
                    'y': self.yAxis.position,
                    'z': self.zAxis.position
                    }
        return position

    def autohome(self):
        self.xAxis.setVelocity(60)
        self.yAxis.setVelocity(45)
        self.xAxis.move('back', -1)
        self.yAxis.move('back', -1)
        self.zAxis.move('back', -1)

    def positionUpdater(self):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        while True:
            try:
                if self.position != self._lastposition:
                    resp = requests.get('http://weblab.deusto.es/labs/flies/push_position', headers=headers)
                    print 'Pushed changes'
                    self._lastposition = self.position
                sleep(0.1)
            except:
                print 'Error pushing changes'
