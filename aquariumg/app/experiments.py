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
        f = open(basedir + "/app/lastFeed", "r")
        self._lastFeed = int(f.read())
        f.close()
        self.lightThread = threading.Thread(target=self._autoController)
        self.lightThread.setDaemon(True)
        self.lightThread.start()

    def tryFeed(self):
        currentTime = datetime.now().hour
        if currentTime - self._lastFeed < 0:
            feedLapse = currentTime + 24 - self._lastFeed
        else:
            feedLapse = currentTime - self._lastFeed
        if feedLapse >= REQUIRED_FEED_LAPSE:
            resp = self._food()
            if resp == 'Fishes feeded':
                f = open(basedir + "/app/lastFeed", "w")
                f.write(str(currentTime))
                f.close()
                self._lastFeed = currentTime
            return True, feedLapse
        else:
            return False, feedLapse

    def _food(self):
        try:
            print 'Feeding fish'
            f = open("/sys/class/gpio/gpio14/value", "w")
            f.write("0")
            f.seek(0)
            time.sleep(1)
            f.write("1")
            f.close()
            f = open(basedir + "/app/lastFeed", "w")
            f.write(str(datetime.now().hour))
            f.close()
            print 'Fish feeded'
            return True
        except:
            return False

    def _autoController(self):
        while self._aquariumOn:
#            try:
                currentHour = datetime.now().hour
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
                if currentHour - self._lastFeed < 0:
                    feedLapse = currentHour + 24 - self._lastFeed
                else:
                    feedLapse = currentHour - self._lastFeed
                if feedLapse >= REQUIRED_AUTOFEED_LAPSE:
                    self._lastFeed = currentHour
                    f = open(basedir + "/app/lastFeed", "w")
                    f.write(str(currentHour))
                    f.close()
                    self._food()
                    time.sleep(30)
                    self._food()
                time.sleep(60)
#            except KeyboardInterrupt:
#                print 'Stopping light control thread'
#                self._aquariumOn = False
#            except:
#                print "Error in light control"

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
