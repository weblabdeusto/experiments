import json, requests
from time import strftime
import os, sys, getopt


def main(argv):
    ip=""
    username=""
  
    try:
        opts, args = getopt.getopt(argv,"h:u:s:",["user=","server="])
    except getopt.GetoptError:
        print 'labSessionCreator.py -u <username> -s <server_ip_adress>'
        sys.exit(2)
    print opts
    print args
    for opt, arg in opts:
        if opt == '-h':
            print 'labSessionCreator.py -u <username> -s <server_ip_adress>'
            sys.exit()
        elif opt in ("-u", "--user"):
            username = arg
        elif opt in ("-s", "--server"):
            print ip
            ip = arg
#    try: 
    session_id,url = createSession(username,ip)
    option = 0
    while option in (0,1,2):
        print 'Session ID: '+ session_id
        print 'URL: '+ url +'\n'
        print '1.         Check user status'
        print '2.         Kick user out'
        print 'Other.     Exit \n'
        option = input('Option: ')
        if option == 1: checkStatus(ip, session_id)
        elif option == 2: kickOut(ip, session_id)
        else: print 'Goodbye'

#    except:
#        print 'labSessionCreator.py -u <username> -s <server_ip_adress>'   


def createSession(user,ip):

    client_initial_data = {
        'back':'http://weblab.deusto.es',
        'url':'http://'+ip+'/weblab/sessions/'
    }

    server_initial_data = {
        'priority.queue.slot.start': strftime("%Y-%m-%d %H:%M:%S")+'.000',
        'priority.queue.slot.length': 200, 
        'request.username': user
    }


    serialized_client_initial_data = json.dumps(client_initial_data)
    serialized_server_initial_data = json.dumps(server_initial_data)
    back_url = json.loads(serialized_client_initial_data).get('back','')
    url = json.loads(serialized_client_initial_data).get('url','')
    data = {
        'client_initial_data' : serialized_client_initial_data,
        'server_initial_data' : serialized_server_initial_data,
        'back' : back_url,
    } 
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    resp = requests.post(url, data=json.dumps(data), headers=headers)
    url=json.loads(resp.content).get('url','')
    session_id = json.loads(resp.content).get('session_id','')

    os.system('nohup google-chrome '+url+ ' &')
    os.system('clear')
    return session_id, url

def checkStatus(ip, session_id):
    os.system('clear')
    url = 'http://'+ ip +'/weblab/sessions/'+ session_id + '/status'
    resp = requests.get(url)
    print 'Response: '+ resp.text

def kickOut(ip, session_id):
    os.system('clear')
    url = 'http://'+ ip +'/weblab/sessions/'+ session_id
    data = {'action' : "delete"} 
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    resp = requests.post(url, data=json.dumps(data), headers=headers)
    print 'Response: '+ resp.text


if __name__ == "__main__":
   main(sys.argv[1:])
