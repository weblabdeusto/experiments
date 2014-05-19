import threading, cv, cv2
#from PIL import Image
import math
import Image
from time import sleep

SHOULD_LEAVE_DATA_THREAD = False


def t_data_thread():
    global SHOULD_LEAVE_DATA_THREAD

    try:
        i = 1
        load = open('/sys/devices/ocp.3/helper.11/AIN6', 'r')
        register = open('/opt/restlite/loadregister', 'w')
        SHOULD_LEAVE_DATA_THREAD = False
        while not SHOULD_LEAVE_DATA_THREAD:
            medida = load.read()
            medidagr = round(((int(medida) - 89.00) * 0.059), 2)
            load.seek(0)
            write = str(i) + ":" + str(medidagr) + "\n"
            register.write(write)
            i += 1
            print write
            sleep(0.03)

        print "Load Register done"
        register.close()
        load.close()
        return
    except:
        print "Imposible create LOAD Reister"
        return


def upthread():
    try:
        #Proceso que subira la bola

        #comprobar si esta en uso el motor
        using = open('/opt/restlite/using', 'r+')
        i = using.read()
        using.seek(0)
        if ('1' in i):
            using.close()
            print 'Motor is using'
            return
            #comprobar si esta arriba o abajo
        updown = open('/opt/restlite/updown', 'r+')
        i = updown.read()
        updown.seek(0)
        if ('1' in i):
            updown.close()
            print 'Ball is UP'
            return

        using.write('1')
        using.seek(0)

        updown.write('1')
        updown.close()

        #Definiendo el sentido del Motor
        #GPIO 39
        print 'GPIO 39 value: 1'
        m0 = open('/sys/class/gpio/gpio39/value', 'w')
        m0.write('1')
        m0.close()
        #GPIO 38
        print 'GPIO 38 value: 1'
        m1 = open('/sys/class/gpio/gpio38/value', 'w')
        m1.write('0')
        m1.close()

        #ACTIVANDO EL MOTOR
        dut = open('/sys/devices/ocp.3/pwm_test_P8_46.10/duty', 'w')
        dut.write('290000')  #29%
        dut.close()
        run = open('/sys/devices/ocp.3/pwm_test_P8_46.10/run', 'w')
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
            #print 'Waiting for BUMPER'
            pass

        run = open('/sys/devices/ocp.3/pwm_test_P8_46.10/run', 'w')
        run.write('0')
        run.close()

        bump.close()

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
    try:
        #Proceso que bajara la bola

        #Activo el hilo para guardar el registro del peso
        r = threading.Thread(target=t_data_thread, name='RegistroLoad')
        r.setDaemon(True)
        r.start()
        sleep(0.5)

        #comprobar si esta en uso el motor
        using = open('/opt/restlite/using', 'r+')
        i = using.read()
        using.seek(0)
        if ('1' in i):
            using.close()
            print 'Motor is using'
            return

        #comprobar si esta arriba o abajo
        updown = open('/opt/restlite/updown', 'r+')
        i = updown.read()
        updown.seek(0)
        if ('0' in i):
            updown.close()
            print 'Ball is DOWN'
            return

        using.write('1')
        using.seek(0)

        updown.write('0')
        updown.close()

        #Definiendo el sentido del Motor
        #GPIO 39
        print 'GPIO 39 value: 1'
        m0 = open('/sys/class/gpio/gpio39/value', 'w')
        m0.write('0')
        m0.close()
        #GPIO 38
        print 'GPIO 38 value: 1'
        m1 = open('/sys/class/gpio/gpio38/value', 'w')
        m1.write('1')
        m1.close()

        #ACTIVANDO EL MOTOR
        dut = open('/sys/devices/ocp.3/pwm_test_P8_46.10/duty', 'w')
        dut.write('240000')  #24%
        dut.close()
        run = open('/sys/devices/ocp.3/pwm_test_P8_46.10/run', 'w')
        run.write('1')
        run.close()
        print 'PWM Runing - Going DOWN'

        #mientras no se den las vueltas necesarias
        hall = open('/sys/class/gpio/gpio66/value', 'r')
        for vueltas in range(0, 120):
            i = hall.read()
            hall.seek(0)
            while '1' in i:
                i = hall.read()
                hall.seek(0)
                #print 'Hall is 1'

            while '0' in i:
                i = hall.read()
                hall.seek(0)
                #print 'Hall is 0'
                #print vueltas

        run = open('/sys/devices/ocp.3/pwm_test_P8_46.10/run', 'w')
        run.write('0')
        run.close()

        using.write('0')
        using.close()

        slowfile = open('/opt/restlite/slow', 'r+')
        slowfile.write("16\n")
        slowfile.close()

        print "Terminar el hilo de registro"
        global SHOULD_LEAVE_DATA_THREAD
        SHOULD_LEAVE_DATA_THREAD = True
        r.join()

        print 'DOWN DONE'
        return
    except:
        print 'DOWN NOT DONE'
        return


def slowthread():
    try:
        #Proceso que subira la bola
        #comprobar si esta en uso el motor
        print "dentro del hilo de DOWN-Slow"

        slowfile = open('/opt/restlite/slow', 'w+')
        i = slowfile.read()
        j = int(i)
        print "La variable en el archivo de control tiene" + i
        if (j < 15):
            j = j + 1
            slowfile.write(j + "\n")
        else:
            slowfile.close()
            return

        slowfile.close()

        using = open('/opt/restlite/using', 'r+')
        i = using.read()
        using.seek(0)
        if ('1' in i):
            using.close()
            print 'Motor is using'
            return

        using.write('1')
        using.seek(0)

        #comprobar si esta arriba o abajo
        updown = open('/opt/restlite/updown', 'r+')
        updown.write('0')
        updown.close()

        #Definiendo el sentido del Motor
        #GPIO 39
        print 'GPIO 39 value: 0'
        m0 = open('/sys/class/gpio/gpio39/value', 'w')
        m0.write('0')
        m0.close()
        #GPIO 38
        print 'GPIO 38 value: 1'
        m1 = open('/sys/class/gpio/gpio38/value', 'w')
        m1.write('1')
        m1.close()

        #ACTIVANDO EL MOTOR
        run = open('/sys/devices/ocp.3/pwm_test_P8_46.10/run', 'w')
        run.write('1')
        run.close()
        print 'PWM Runing - Going DOWN'

        #mientras no se den las vueltas necesarias
        hall = open('/sys/class/gpio/gpio66/value', 'r')
        for vueltas in range(0, 5):
            i = hall.read()
            hall.seek(0)
            while '1' in i:
                i = hall.read()
                hall.seek(0)
            print 'Hall is 1'

            while '0' in i:
                i = hall.read()
                hall.seek(0)
            print 'Hall is 0'
            print vueltas

        run = open('/sys/devices/ocp.3/pwm_test_P8_46.10/run', 'w')
        run.write('0')
        run.close()

        using.write('0')
        using.close()

        print 'DOWNSLOW DONE'
        return
    except:
        print 'DOWNSLOW NOT DONE'
        return


def imagethread(ruta):
    try:
        print 'Path: ' + ruta
        capture = cv.CaptureFromCAM(0)
        print "Capturando de CAM0"
        cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT, 896)
        cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH, 1600)
        print "Propiedades de CAM0"
        if not capture:
            print 'Error en webcam'
            return 0
        photo = cv.QueryFrame(capture)
        print "Adquiriendo Frame"
        if not photo:
            print 'Error en foto'
            return 0
            #font = cv2.FONT_HERSHEY_SIMPLEX
        #print "Fuente Seleccionada"
        #cv2.PutText(photo, 'PRUEBA TEXTO', (50,50), font, 4,(255,0,0))
        #cv.putText(photo, "Press ESC to close.", (5, 25), cv.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255))
        #cv.PutText(photo, 'PRUEBA DE TREXTO', (100,100), FONT_HERSHEY_SIMPLEX, (0,255,0))
        #print "Texto puesto"
        cv.SaveImage(ruta, photo)
        print "Imagen salvada"
        return
    except:
        print 'PHOTO NOT DONE'
        return


def prexecute():
    #Configuracion del PWM
    #POLARIDAD
    try:
        pola = open('/sys/devices/ocp.3/pwm_test_P8_46.10/polarity', 'w')
        pola.write('0')
        pola.close()
        #PERIODO
        perio = open('/sys/devices/ocp.3/pwm_test_P8_46.10/period', 'w')
        perio.write('1000000')
        perio.close()
        #DUTTY CICLE
        dut = open('/sys/devices/ocp.3/pwm_test_P8_46.10/duty', 'w')
        dut.write('290000')  #29%
        dut.close()
        run = open('/sys/devices/ocp.3/pwm_test_P8_46.10/run', 'w')
        run.write('0')
        run.close()

        using = open('/opt/restlite/using', 'w')
        updown = open('/opt/restlite/updown', 'w')
        using.write('0')
        updown.write('0')
        using.close()
        updown.close()

        print 'Preexecute DONE!!'
    except:
        print 'Preexecute NOT DONE!!'


def up(env, start_response):
    print "[DBG]: UP RECEIVED"
    #start_response('200 OK', [('Content-Type', 'text/plain')])
    u = threading.Thread(target=upthread, name='SubidaMotor')
    u.setDaemon(True)
    u.start()
    return 'BALL_UP'


def down(env, start_response):
    #start_response('200 OK', [('Content-Type', 'text/plain')])
    d = threading.Thread(target=downthread, name='BajadaMotor')
    d.setDaemon(True)
    d.start()
    return 'BALL_DOWN'


def slow(env, start_response):
    #start_response('200 OK', [('Content-Type', 'text/plain')])
    print "dentro de la peticion de DOWN-Slow"
    d = threading.Thread(target=slowthread, name='BajadaDespacioMotor')
    d.setDaemon(True)
    d.start()
    return 'BALL_DOWNSLOW'


def image(env, start_response):
    #start_response('200 OK', [('Content-Type', 'text/plain')])
    start_response('200 OK', [('Content-type', 'image/jpeg')])
    try:
        from datetime import datetime
        #ruta = '/var/www/images/' + datetime.now().strftime('%d%m%y%H%M%S') + '.jpg'
        ruta = '/var/www/images/hdpicture.jpg'
        img = threading.Thread(target=imagethread, args=(ruta,), name='PhotoThread')
        img.setDaemon(True)
        img.start()
        while img.isAlive():
            print "Tomando foto..."
    except:
        raise restlite.Status, '400 Error capturing Image'
    try:
        with open(ruta, 'rb') as f:
            result = f.read()
    except:
        raise restlite.Status, '400 Error Reading File'
    return [result]


def load(env, start_response):
    try:
        loadm = open('/sys/devices/ocp.3/helper.11/AIN6', 'r')
        totval = 0
        for med in range(0, 30):
            val = loadm.read()
            loadm.seek(0)
            totval = totval + int(val)
            # print val
        #print med
        #print totval
        #print "--"
        #totval = level.read()
        loadm.close()
        totval = totval / (med + 1)
        #print totval
        return 'TOTAL_LOAD=' + str(totval)
    except:
        #		raise restlite.Status, '400 Error capturing level'
        return 'TOTAL_LOAD=0'


def level(env, start_response):
    #start_response('200 OK', [('Content-Type', 'text/plain')])
    level = open('/sys/devices/ocp.3/helper.11/AIN4', 'r')

    totval = 0
    try:
        for med in range(0, 30):
            val = level.read()
            level.seek(0)
            totval = totval + int(val)
            #print med
        #print totval
        #print "--"
        #totval = level.read()
        level.close()
        totval = totval / (med + 1)
        #print totval
        return 'WATERLEVEL=' + str(totval)
    except:
        #		raise restlite.Status, '400 Error capturing level'
        return 'WATERLEVELERROR=0'  #+ str(totval)


def plotload(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    try:
        ruta = '/opt/restlite/loadregister'
        register = open(ruta, 'r')
        result = register.read()
        register.close()
    except:
        raise restlite.Status, '400 Error retrieving data'
    return result


def plotlevel(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])


def object(env, start_response):
    #start_response('200 OK', [('Content-Type', 'text/plain')])
    nombre = "PingPong ball fill off Water"
    try:
        radio = 4
        volumen = round((4.00 / 3.00) * math.pi * (radio ** 3.00), 2)
        masa = load(env, start_response)
        masa = masa.split("=")
        masagr = round(((int(masa[1]) - 89.00) * 0.059), 2)
        peso = round((masagr / 1000.00) * 9.80, 2)
        densidad = round(masagr / volumen, 2)
        dobj = "Nombre=" + nombre + "," + "Radio(cm)=" + str(radio) + "," + "Volumen(cm3)=" + str(volumen) + "," \
               + "Masa(g)=" + str(masagr) + "," + "Peso(N)=" + str(peso) + "," + "Densidad(g/cm3)=" + str(densidad)
    except:
        dobj = "Nombre=" + nombre + "," + "Radio(cm)=4," + "Volumen(cm3)=0," + "Peso(g)=0," + "Masa(N)=0," + "Densidad(g/cm3)=0"
        raise restlite.Status, '400 Error retrieving data'
    return dobj


def liquid(env, start_response):
    #start_response('200 OK', [('Content-Type', 'text/plain')])
    nombre = "Colored Water"
    try:
        radio = 6.5
        densidad = 1
        altura = level(env, start_response)
        altura = altura.split("=")
        alturacm = round((8.00 - ((int(altura[1]) - 935.00) / 85.00)) * 2.54, 2)
        volumen = round(math.pi * (radio ** 2) * alturacm, 2)
        dobj = "Nombre=" + nombre + "," + "Altura(cm)=" + str(alturacm) + "," + "Volumen(cm3)=" + str(
            volumen) + "," + "Densidad(g/cm3)=" + str(densidad)
        return dobj
    except:
        dobj = "Nombre=" + nombre + ",Altura=0,Volumen(cm3)=0,Densidad(g/cm3)=0"
        #raise restlite.Status, '400 Error retrieving data'
        return dobj


routes = [
    (r'GET /up', up),
    (r'GET /down', down),
    (r'GET /slow', slow),
    (r'GET /image', image),
    (r'GET /load', load),
    (r'GET /level', level),
    (r'GET /plotload', plotload),
    (r'GET /plotlevel', plotlevel),
    (r'GET /object', object),
    (r'GET /liquid', liquid),
]

import restlite

from wsgiref.simple_server import make_server

httpd = make_server('', 2001, restlite.router(routes))

try:
    prexecute()
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
