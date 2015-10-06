import time
import threading
from datetime import datetime
from config import basedir, LIGHT_START_TIME, LIGHT_ON_TIME, REQUIRED_FEED_LAPSE, REQUIRED_AUTOFEED_LAPSE


class Aquarium(object):

    def __init__(self, lightStartTime=LIGHT_START_TIME, lightOnTime=LIGHT_ON_TIME):
        self.lightOnTime = lightOnTime
        self.lightStartTime = lightStartTime
        self._lightManualOn = False
        self._lightOn = False
        self._aquariumOn = True
        try:
            print basedir + "/app/lastFeed"
            f = open(basedir + "/app/lastFeed", "r")
            self._lastFeed = datetime.strptime(f.read(),"%Y-%m-%d %H:%M")
            f.close()
        except:
            print 'cant read feed log'
            self._food()
        self.lightThread = threading.Thread(target=self._autoController)
        self.lightThread.setDaemon(True)
        self.lightThread.start()

    def tryFeed(self):
        currentTime = datetime.now()
        if (currentTime-self._lastFeed).seconds >= REQUIRED_FEED_LAPSE*60*60:
            if self._food():
                return {'success':True}
            else:
                return {'success':False, 'last':(currentTime-self._lastFeed).seconds}
        else:
            return {'success':False, 'last':(currentTime-self._lastFeed).seconds}

    def _food(self):
        try:
            print 'Feeding fish'
            f = open("/sys/class/gpio/gpio18/value", "w")
            f.write("0")
            f.seek(0)
            time.sleep(5)
            f.write("1")
            f.close()
            self._lastFeed = datetime.now()
            f = open(basedir + "/app/lastFeed", "w")
            f.write(self._lastFeed.strftime("%Y-%m-%d %H:%M"))
            f.close()
            print 'Fish feeded'
            return True
        except:
            return False

    def _autoController(self):
        while self._aquariumOn:
            try:
                currentHour = datetime.now().hour
                currentTime = datetime.now()
                if (currentHour >= self.lightStartTime) and (currentHour < self.lightStartTime + self.lightOnTime):
                    f = open("/sys/class/gpio/gpio2/value", "w")
                    f.write("1")
                    f.close()
                    self._lightOn = True
                else:
                    if self._lightManualOn != True:
                        f = open("/sys/class/gpio/gpio2/value", "w")
                        f.write("0")
                        f.close()
                        self._lightOn = False
                    else:
                        print 'Light turned on by user'
                if (currentTime-self._lastFeed).seconds >= REQUIRED_AUTOFEED_LAPSE*60*60:
                    self._food()
                    time.sleep(30)
                    self._food()
                time.sleep(60)
            except:
                time.sleep(10)
                print "Error in light control"
        print "Light controller off"

    def _lightOneMinute(self):
        if self._lightOn == False:
            self._lightManualOn = True
            self._lightOn = True
            f2 = open("/sys/class/gpio/gpio2/value", "w")
            f2.write("1")
            f2.seek(0)
            time.sleep(60)
            f2.write("0")
            f2.close()
            self._lightManualOn = False
            self._lightOn = False
            print "Done"
        else:
            print "Light is on"

    def turnLightOn(self):
        try:
            if self._lightOn == True: 
                return False
            lightThread = threading.Thread(target=self._lightOneMinute)
            lightThread.start()
            return True
        except:
            print "Error starting light thread"
            return False


    def status(self):
        if (datetime.now()-self._lastFeed).seconds >= REQUIRED_FEED_LAPSE*60*60:
            need = True
        else:
            need = False
        return {'light':{'status':self._lightOn,
                         'manual':self._lightManualOn
                         },
                'food':{'need':need,
                        'last':(datetime.now()-self._lastFeed).seconds
                        }}
