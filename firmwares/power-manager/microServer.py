
import json
from powerManager import Manager

def launchHTTPServer(manager):

    from BaseHTTPServer import BaseHTTPRequestHandler

    class RequestHandler(BaseHTTPRequestHandler):

        def do_GET(self):
            if '/restart' in self.path:
                try:
                    path = self.path.split('&')
                    labIndex = int(path[1])
                    if labIndex >= len(manager.labs):
                        print 'Index out of range'
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write('Index out of range')
                    # Begin the response
                    else:
                        self.send_response(200)
                        self.end_headers()
                        print 'Asking for position on lab: ' + manager.labs[labIndex]['name']
                        self.wfile.write(json.dumps(manager.restart(labIndex)))
                except:
                    print 'Bad request'
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write('Bad request')
            elif self.path=='/status':
                self.send_response(200)
                self.end_headers()
                print 'Status checking'
                self.wfile.write('')
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write('Bad request')

    from BaseHTTPServer import HTTPServer

    server = HTTPServer(('0.0.0.0', 8080), RequestHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print '\nServer stopped'
        manager.run = False

if __name__ == '__main__':
    manager = Manager()
    launchHTTPServer(manager)
