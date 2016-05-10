from config import labs, DEBUG
from threading import Thread
import logging
import requests
import time
if not DEBUG:
    import pifacedigitalio

class Manager(object):

    def __init__(self):
        if not DEBUG:
            self.pfd = pifacedigitalio.PiFaceDigital()
        self.labs = labs
        self.checkingThread = Thread(target=self.checker)
        logging.basicConfig(filename='logs/status.log',
                            level=logging.INFO,
                            format='%(asctime)s %(levelname)s: %(message)s'
                            )
        logging.info('[Power manager]: Started')
        self.run = True
        self.checkingTime = 2 #Time in minutes
        self.checkingThread.setDaemon(True)
        self.checkingThread.start()

    def checker(self):
        while self.run:
            for lab in self.labs:
                response = requests.get('http://'+lab['ip']+lab['path'],timeout=5)
                if response.status_code == 200:
                    logging.info('[%s]: Lab is up',lab['name'])
                    if response.content == 'Error':
                        logging.warning('[%s]: report error...', lab['name'])
                        try:
                            if not DEBUG:
                                self.pfd.relays[lab['relay']].value = 1
                                time.sleep(2)
                                self.pfd.relays[lab['relay']].value = 0

                            logging.info('[%s]: Lab restarted', lab['name'])
                        except:
                            logging.warning('[%s]:Restarting failed', lab['name'])
                    else:
                        logging.info('[%s]: No error reported',lab['name'])

                else:
                    logging.warning('[%s]: Lab is down,restarting...', lab['name'])
                    try:
                        if not DEBUG:
                            self.pfd.relays[lab['relay']].value = 1
                            time.sleep(2)
                            self.pfd.relays[lab['relay']].value = 0
                        logging.info('[%s]: Lab restarted', lab['name'])
                    except:
                        logging.warning('[%s]:Restarting failed', lab['name'])

            time.sleep(self.checkingTime*60)

    def restart(self,lab):

        logging.warning('[%s]: Restarting lab', self.labs[lab]['name'])
        try:
            if not DEBUG:
                self.pfd.relays[self.labs[lab]['relay']].value = 1
                time.sleep(2)
                self.pfd.relays[self.labs[lab]['relay']].value = 0
        except:
            logging.warning('[%s]: Restart failed', self.labs[lab]['name'])
        logging.info('[%s]: Restarted', self.labs[lab]['name'])
        return 'Success'
