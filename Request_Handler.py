from http.server import HTTPServer, BaseHTTPRequestHandler
from Publisher import Publisher as p
import os, threading, json

class Request_Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(self.path)
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=UTF-8')            
            self.end_headers()
            response = ''
            with open('public_html/index.html', 'r') as f:
                line = f.readline()
                while line:
                    response += line
                    line = f.readline()     
                self.wfile.write(bytes(response, 'utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Content-Length', os.path.getsize('public_html'+self.path))
            self.end_headers()
            with open('public_html'+self.path, 'rb') as f:
                self.wfile.write(f.read())

    def do_POST(self):        
        if self.path == '/sensor':
            length = int(self.headers['Content-Length'])
            request_data = self.rfile.read(length)
            request_data = request_data.decode('utf-8')
            print(json.loads(request_data))
            self.send_response(200)
            #print(self.rfile.read())
            #cli = p('fsa', 'localhost', 8000)
            #x = {}
            #x['data'] = 'batata'
            #threading.Thread(target=cli.publish, args=(x,)).start()
            #self.send_response(200)
            #self.wfile.write(b'Sensor created')

    def do_PUT(self):
        if self.path == '/sensor':
            print(self.headers)
            self.send_response(200)
            #self.wfile.write(b'Received')