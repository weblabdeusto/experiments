import requests
import os
import time
import logging

#Settup logging handler
logging.basicConfig(filename='/home/pi/experiments/unmanaged/zumo1/logs/network.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s'
)
logging.info('[Network checker]: Started')


while True:
    try:
        response = requests.get('http://192.168.0.2/labs/ardulab/test')
        if response.status_code == 200:
            logging.info('[Network checker]: Host is up')
            print 'Host is up'
        else:
            print 'host is down'
            logging.info('[Network checker]: Host is down')
            response= os.system('service networking restart')
            logging.info(response)

    except:
        logging.info('[Network checker]: Exception...Host is down')
        print 'Exception...host is down'
        response= os.system('service networking restarcdt')
        logging.info(response)

    time.sleep(60)
