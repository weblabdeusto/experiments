import threading, cv, cv2, operator, collections
import math
from time import sleep,time
import numpy as np
from datetime import datetime
from datetime import timedelta

#Configuracion:

caja=1

if caja==1:
	plataform='BBB'
	sentido=0
	cell=True
elif caja==2:
	plataform='BB'
	sentido=1
	cell=True
elif caja==3:
	plataform='BBB'
	sentido=1
	cell=True
elif caja==4:
	plataform='BBB'
	sentido=1
	cell=True
elif caja==5:
	plataform='BBB'
	sentido=0
	cell=False
elif caja==6:
	plataform='BBB'
	sentido=0
	cell=True
elif caja==7:
	plataform='BBB'
	sentido=0
	cell=True
else:
	print 'Error configuracion'

if plataform=='BBB':
	rutaAin='/sys/devices/ocp.3/helper.12/'
	rutaPwm='/sys/devices/ocp.3/pwm_test_P8_46.11/'
else:
	rutaAin='/sys/devices/ocp.3/helper.11/'
	rutaPwm='/sys/devices/ocp.3/pwm_test_P8_46.10/'


SHOULD_LEAVE_DATA_THREAD = False
fload=open('/opt/restlite/realLoad','r')
realload = fload.read()
fload.close()
lastDev = 0.05
lastDatetime = datetime.now() - timedelta(0,1801)

def t_data_thread(): #para hacer record de datos del peso mientras se baja la bola
    global SHOULD_LEAVE_DATA_THREAD
    try:
        i = 1
        register = open('/opt/restlite/loadregister', 'w')
        SHOULD_LEAVE_DATA_THREAD = False
        while not SHOULD_LEAVE_DATA_THREAD:
            medidagr = load()[11:]
            write = str(i) + ":" + str(medidagr) + "\n"
            register.write(write)
            i += 1
            print write
            sleep(0.03)

        print "Load Register done"
        register.close()
        return
    except:
        print "Imposible create LOAD Reister"
        return

def upthread():
    global rutaPwm
    global sentido
    try:
        #Proceso que subira la bola

        #comprobar si esta en uso el motor
        using = open('/opt/restlite/using', 'r')
        i = using.read()
        using.seek(0)
        if ('1' in i):
            print 'Motor is using'
            return
            #comprobar si esta arriba o abajo
        using.close()
	updown = open('/opt/restlite/updown', 'r')
        i = updown.read()
        if ('1' in i):
            print 'Ball is UP'
            return
	updown.close()

	using=open('/opt/restlite/using','w')
        using.write('1')
        using.close()
	
	updown=open('/opt/restlite/updown','w')
        updown.write('1')
        updown.close()

	

        #Definiendo el sentido del Motor
        #GPIO 39
        print 'GPIO 39 value: 0'
        m0 = open('/sys/class/gpio/gpio39/value', 'w')
	if sentido==0:
		m0.write('0')
	else:
		m0.write('1')
        m0.close()
        #GPIO 38
        print 'GPIO 38 value: 1'
        m1 = open('/sys/class/gpio/gpio38/value', 'w')
	if sentido==0:
		m1.write('1')
	else:
		m1.write('0')
        m1.close()

        #ACTIVANDO EL MOTOR
        dut = open(rutaPwm+'duty', 'w')
        dut.write('400000')  #40%
        dut.close()
        run = open(rutaPwm+'run', 'w')
        run.write('1')
        run.close()
        print 'PWM Runing - Going UP'

        #mientras no se toque el BUMPER
        bump = open('/sys/class/gpio/gpio67/value', 'r')
        i = bump.read()
        bump.seek(0)
        while ('1' in i):
            i = bump.read()
            bump.seek(0)
            pass

        #Definiendo el sentido del Motor
        #GPIO 39
        print 'GPIO 39 value: 1'
        m0 = open('/sys/class/gpio/gpio39/value', 'w')
        if sentido==0:
                m0.write('1')
        else:
                m0.write('0')
        m0.close()
        #GPIO 38
        print 'GPIO 38 value: 0'
        m1 = open('/sys/class/gpio/gpio38/value', 'w')
        if sentido==0:
                m1.write('0')
        else:
                m1.write('1')
        m1.close()

        #ACTIVANDO EL MOTOR
        dut = open(rutaPwm+'duty', 'w')
        dut.write('240000')  #24%
        dut.close()
        run = open(rutaPwm+'run', 'w')
        run.write('1')
        run.close()
        print 'PWM Runing - Going DOWN'
        start=time()

        hall = open('/sys/class/gpio/gpio66/value', 'r')
        for vueltas in range(0, 5):
            i = hall.read()
            hall.seek(0)
            while '1' in i:
                i = hall.read()
                hall.seek(0)
                if time()-start>=5:
                        break
            while '0' in i:
                i = hall.read()
                hall.seek(0)
                if time()-start>=5:
                        break
            if time()-start>=5:
                break


        run = open(rutaPwm+'run', 'w')
        run.write('0')
        run.close()

        bump.close()
	using=open('/opt/restlite/using','w')
        using.write('0')
        using.close()

        slowfile = open('/opt/restlite/slow', 'r+')
        slowfile.write("0\n")
        slowfile.close()

        print 'UP DONE'
        return
    except:
        print 'UP NOT DONE'
        return


def downthread():
    global rutaPwm
    global cell
    if cell:
	steps=140
    else:
	steps=120
    try:
        #Proceso que bajara la bola

        #comprobar si esta en uso el motor
        using = open('/opt/restlite/using', 'r')
        i = using.read()
        if ('1' in i):
            print 'Motor is using'
            return
	using.close()
        #comprobar si esta arriba o abajo
        updown = open('/opt/restlite/updown', 'r')
        i = updown.read()
        if ('0' in i):
            print 'Ball is DOWN'
            return
	updown.close()
	#Activo el hilo para guardar el registro del peso
        r = threading.Thread(target=t_data_thread, name='RegistroLoad')
        r.setDaemon(True)
        r.start()
        sleep(0.5)

	using=open('/opt/restlite/using','w')
        using.write('1')
        using.close()

        #Definiendo el sentido del Motor
        #GPIO 39
        print 'GPIO 39 value: 1'
        m0 = open('/sys/class/gpio/gpio39/value', 'w')
	if sentido==0:
		m0.write('1')
	else:
		m0.write('0')
        m0.close()
        #GPIO 38
        print 'GPIO 38 value: 0'
        m1 = open('/sys/class/gpio/gpio38/value', 'w')
	if sentido==0:        
		m1.write('0')
	else:
		m1.write('1')
        m1.close()

        #ACTIVANDO EL MOTOR
        dut = open(rutaPwm+'duty', 'w')
        dut.write('240000')  #24%
        dut.close()
        run = open(rutaPwm+'run', 'w')
        run.write('1')
        run.close()
        print 'PWM Runing - Going DOWN'
	start=time()
        #mientras no se den las vueltas necesarias
        hall = open('/sys/class/gpio/gpio66/value', 'r')
        for vueltas in range(0, steps):
            i = hall.read()
            hall.seek(0)
            while '1' in i:
                i = hall.read()
                hall.seek(0)
		if time()-start>=1.9:
			break
            while '0' in i:
                i = hall.read()
                hall.seek(0)
		if time()-start>=1.9:
			break
	    if time()-start>=1.9:
		break

        # detengo el motor
        run = open(rutaPwm+'run', 'w')
        run.write('0')
        run.close()
	
        updown=open('/opt/restlite/updown','w')
        updown.write('0')
        updown.close()


	using=open('/opt/restlite/using','w')
        using.write('0')
        using.close()

        print "Terminar el hilo de registro"
        global SHOULD_LEAVE_DATA_THREAD
        SHOULD_LEAVE_DATA_THREAD = True
        r.join()

        print 'DOWN DONE'
        return
    except:
        print 'DOWN NOT DONE'
        return

def prexecute():
    #Configuracion del PWM inicial se ejecuta al principio
    global rutaPwm
    global realload

    try:
        #POLARIDAD
        pola = open(rutaPwm+'polarity', 'w')
        pola.write('0')
        pola.close()
        #PERIODO
        perio = open(rutaPwm+'period', 'w')
        perio.write('1000000')
        perio.close()
        #DUTTY CICLE
        dut = open(rutaPwm+'duty', 'w')
        dut.write('290000')  #29%
        dut.close()
        run = open(rutaPwm+'run', 'w')
        run.write('0')
        run.close()

        #archivos para controlar donde esta la bola y si se esta usando el motor
        using = open('/opt/restlite/using', 'w')
        #updown = open('/opt/restlite/updown', 'w')
        using.write('0')
        #updown.write('0')
        using.close()
        #updown.close()

	realloadfile = open('/opt/restlite/realLoad', 'r')
        realload = float(realloadfile.read())
        realloadfile.close()

        print 'Preexecute DONE!!'
    except:
        print 'Preexecute NOT DONE!!'


def up():
    print "[DBG]: UP RECEIVED"
    u = threading.Thread(target=upthread, name='SubidaMotor')
    u.setDaemon(True)
    u.start()
    return 'BALL_UP'


def down():
    d = threading.Thread(target=downthread, name='BajadaMotor')
    d.setDaemon(True)
    d.start()
    return 'BALL_DOWN'


def slow():
    print "dentro de la peticion de DOWN-Slow"
    d = threading.Thread(target=slowthread, name='BajadaDespacioMotor')
    d.setDaemon(True)
    d.start()
    return 'BALL_DOWNSLOW'


def image():

    	try:
        	with open('/var/www/images/hdpicture.jpg', 'rb') as f:
          	  	result = f.read()	 
		return result
    	except:
                print "Exception caught"
        	return 0

def load():
	global realload
	global lastDatetime
	global lastDev
	global rutaAin
	global cell

	if cell:
	    try:
		ahora = datetime.now()
		updown = open('/opt/restlite/updown', 'r')
		i = updown.read()
		updown.close()
		loadm = open(rutaAin+'AIN6', 'r')
		totval = 0
		for med in range(0, 30):
		    val = loadm.read()
		    loadm.seek(0)
		    totval = totval + int(val)
		loadm.close()
		totval = totval / (med + 1)
		print totval
		print realload
		if (((ahora-lastDatetime).total_seconds() > 1800) and (i == '1')):
		    lastDev = float(realload) / (totval - 81)
		    lastDatetime = datetime.now()
		print lastDev
		totval = round(((totval - 81) * lastDev), 2)
		return 'TOTAL_LOAD=' + str(totval)
	    except:
		return 'TOTAL_LOAD=0'
	else:
		import random
		updown = open('/opt/restlite/updown', 'r')
        	i = updown.read()
		updown.close()
		if i=='1':
			return 'TOTAL_LOAD=' + str(round(realload+(random.random()/2),2))
		else:
			return 'TOTAL_LOAD=' + str(round(0.9+(random.random()/2)-0.7,2))
			

def level():
    try:    
	levelf=open('/opt/restlite/level','r')
	level=levelf.readline()
	levelf.close()
	if level!='0':
		return 'WATERLEVEL=' + level
	else:
		return 'WATERLEVELERROR=0'
    except:
	return 'WATERLEVELERROR=0'	

def plotload():

    ruta = '/opt/restlite/loadregister'
    register = open(ruta, 'r')
    result = register.read()
    register.close()
    return result

def status():
    f=open('/opt/restlite/updown','r')
    pos=f.read()
    f.close()
    f=open('/opt/restlite/using','r')
    using=f.read()
    f.close()
    if(pos=='1')and(using=='0'):
        return 'BALL_UP'
    elif(pos=='1')and(using=='1'):
        return 'BALL_GOING_DOWN'
    elif(pos=='0')and(using=='0'):
        return 'BALL_DOWN'
    elif(pos=='0')and(using=='1'):
        return 'BALL_GOING_UP'
    else:
        return 'ERROR'

import SocketServer
import SimpleHTTPServer
PORT = 80
IP = ''

class CustomHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path=='/up':
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(up())
            return
	elif self.path=='/down':
	    self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(down())
            return
	elif self.path=='/slow':
	    self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(slow())
            return
	elif self.path=='/image':
	    self.send_response(200)
            self.send_header('Content-type','image/jpeg')
            self.end_headers()
            self.wfile.write(image())
            return
	elif self.path=='/load':
	    self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(load())
            return
	elif self.path=='/level':
	    self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(level())
            return
	elif self.path=='/status':
	    self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(status())
            return
	elif self.path=='/plotload':
	    self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(plotload())
            return    
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self) #dir listing

httpd = SocketServer.ThreadingTCPServer((IP, PORT),CustomHandler)

print 'Port=',PORT

try:
    prexecute()
    httpd.serve_forever()
except KeyboardInterrupt:
    pass

