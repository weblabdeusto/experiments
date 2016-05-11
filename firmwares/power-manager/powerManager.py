from config import labs, DEBUG
from threading import Thread
import logging
import requests
import time
from datetime import datetime
if not DEBUG:
    import pifacedigitalio

class Manager(object):

    def __init__(self):
        #Init piface object
        if not DEBUG:
            self.pfd = pifacedigitalio.PiFaceDigital()
        #get lab data
        self.labs = labs
        #Settup logging handler
        logging.basicConfig(filename='logs/status.log',
                            level=logging.INFO,
                            format='%(asctime)s %(levelname)s: %(message)s'
                            )
        logging.info('[Power manager]: Started')

        #Atributtes
        self.run = True
        self.checkingTime = 1 #Time in minutes for status checking
        self.timeout = 5  #Time in minutes for restarting after server down detected

        #Start thread
        self.checkingThread = Thread(target=self.checker)
        self.checkingThread.setDaemon(True)
        self.checkingThread.start()

    def _shutDownRelay(self,index):
        if not DEBUG:
            self.pfd.relays[index].value = 1
            time.sleep(2)
            self.pfd.relays[index].value = 0
        else:
            print 'Relay ON'
            time.sleep(2)
            print 'Relay OFF'

    def checker(self):

        while self.run:
            for lab in self.labs:
                try:
                    response = requests.get('http://'+lab['ip']+lab['path'],timeout=10)
                    if response.status_code == 200:
                        logging.info('[%s]: Lab is up',lab['name'])
                        if response.content == 'Error':
                            logging.warning('[%s]: report error...', lab['name'])
                            try:
                                self._shutDownRelay(lab['relay'])
                                logging.info('[%s]: Lab restarted', lab['name'])
                            except:
                                logging.warning('[%s]: Restarting failed', lab['name'])
                        else:
                            logging.info('[%s]: No error reported',lab['name'])

                    else:
                        if lab['lastDown'] == None:
                            lab['lastDown'] = datetime.now()
                            logging.warning('[%s]: Lab is down,starting countdown for restart...', lab['name'])

                        print (datetime.now()-lab['lastDown']).seconds
                        count = (datetime.now()-lab['lastDown']).seconds
                        logging.warning('[%s]: %d seconds for shutting power down...', lab['name'],self.timeout*60 - count)
                        if count >= self.timeout*60:
                            try:
                                lab['lastDown'] = datetime.now()
                                logging.warning('[%s]: Shutting power down!', lab['name'])
                                self._shutDownRelay(lab['relay'])
                            except:
                                logging.warning('[%s]: Restarting failed', lab['name'])
                except:
                    if lab['lastDown'] == None:
                        lab['lastDown'] = datetime.now()
                        logging.warning('[%s]: Lab is down,starting countdown for restart...', lab['name'])

                    print (datetime.now()-lab['lastDown']).seconds
                    count = (datetime.now()-lab['lastDown']).seconds
                    logging.warning('[%s]: %d seconds for shutting power down...', lab['name'],self.timeout*60 - count)
                    if count >= self.timeout*60:
                        try:
                            lab['lastDown'] = datetime.now()
                            logging.warning('[%s]: Shutting power down!', lab['name'])
                            self._shutDownRelay(lab['relay'])
                        except:
                            logging.warning('[%s]: Restarting failed', lab['name'])

            time.sleep(self.checkingTime*60)


    def restart(self,lab):
        logging.info('[%s]: Restarting lab by user request', self.labs[lab]['name'])
        try:
            self.labs[lab]['lastDown'] = datetime.now()
            self._shutDownRelay(self.labs[lab]['relay'])
        except:
            logging.warning('[%s]: Restart failed', self.labs[lab]['name'])
        logging.info('[%s]: Restarted', self.labs[lab]['name'])
        return 'Success'

