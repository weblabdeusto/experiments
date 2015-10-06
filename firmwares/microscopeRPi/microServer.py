import json
from experiment import Microscope

def launchHTTPServer(microscope):

    from BaseHTTPServer import BaseHTTPRequestHandler
    import cgi

    class RequestHandler(BaseHTTPRequestHandler):

        def do_GET(self):
            if self.path == '/position':
            # Begin the response
                self.send_response(200)
                self.end_headers()
                print 'Asking for position'
#                self.wfile.write(json.dumps({'x':100,'y':2,'z':3}))
                self.wfile.write(json.dumps(microscope.position))

            elif self.path == '/autohome':
                self.send_response(200)
                self.end_headers()
                print 'Autohome'
                self.wfile.write(json.dumps(microscope.autohome()))

            elif self.path == '/stopall':
                self.send_response(200)
                self.end_headers()
                print 'Stop all'
                try:
                    microscope.xAxis.stop()
                    microscope.yAxis.stop()
                    microscope.zAxis.stop()
                    self.wfile.write('Done')
                except:
                    self.wfile.write('Error')

        def do_POST(self):
            # Parse the form data posted
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST',
                         'CONTENT_TYPE':self.headers['Content-Type'],
                         })
            if self.path == '/move':
            # Begin the response
                self.send_response(200)
                self.end_headers()
                direction = json.loads(form.value).get('direction','')
                milimeters = json.loads(form.value).get('dist','')
                axis = json.loads(form.value).get('axis','')
                if axis == 'x':
                    self.wfile.write(microscope.xAxis.move(direction, float(milimeters)))
#                     self.wfile.write('Testing X')
                elif axis == 'y':
                    self.wfile.write(microscope.yAxis.move(direction, float(milimeters)))
#                    self.wfile.write('Testing Y')
                elif axis == 'z':
                    self.wfile.write(microscope.zAxis.move(direction, float(milimeters)))
#                    self.wfile.write('Testing Z')
                self.wfile.write('Axis %s moving %s %s milimeters'%(axis,direction,milimeters))
                print ('Axis %s moving %s %s milimeters'%(axis,direction,milimeters))
                return
            if self.path == '/moveall':
                # Begin the response
                self.send_response(200)
                self.end_headers()
                newx = float(json.loads(form.value).get('x',''))
                newy = float(json.loads(form.value).get('y',''))
                newz = float(json.loads(form.value).get('z',''))
                print 'Recived x:%2f, y:%2f, z:%2f'%(newx,newy,newz)

                x = microscope.xAxis.position
                y = microscope.yAxis.position
                z = microscope.zAxis.position
                if newx > x:
                    self.wfile.write(microscope.xAxis.move('forward',newx-x))
                elif newx < x:
                    self.wfile.write(microscope.xAxis.move('back',x-newx))
                if newy > y:
                    self.wfile.write(microscope.yAxis.move('forward',newy-y))
                elif newy < y:
                    self.wfile.write(microscope.yAxis.move('back',y-newy))
                if newz > z:
                    self.wfile.write(microscope.zAxis.move('forward',newz-z))
                elif newz < z:
                    self.wfile.write(microscope.zAxis.move('back',z-newz))
                return
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write('Error')

    from BaseHTTPServer import HTTPServer

    server = HTTPServer(('0.0.0.0', 8083), RequestHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()

if __name__ == '__main__':
    microscope = Microscope()
#    microscope = 'DEBUG'
    launchHTTPServer(microscope)
