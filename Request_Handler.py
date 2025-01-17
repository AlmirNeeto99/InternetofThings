from http.server import HTTPServer, BaseHTTPRequestHandler
from Sensor_Handler import handle_sensor_request
from Actuator_Handler import handle_actuator_request
import os, threading, json, secrets

def handle_request(broker):
    class Request_Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            split_path = self.path.split('/')
            # return the first page of application...
            if self.path == '/':
                self.send_response(200) # OK
                self.send_header('Content-Type', 'text/html; charset=UTF-8')            
                self.end_headers()
                response = ''
                with open('public_html/index.html', 'r') as f:
                    line = f.readline()
                    while line:
                        response += line
                        line = f.readline()     
                    self.wfile.write(bytes(response, 'utf-8'))
                return
            elif self.path == '/sensor':
                # return the page that list all sensors...
                self.send_response(200) # OK
                self.send_header('Content-Type', 'text/html; charset=UTF-8')            
                self.end_headers()
                response = ''
                # read all lines of a html page and return it to browser...
                with open('public_html/sensor.html', 'r') as f:
                    line = f.readline()
                    while line:
                        response += line
                        line = f.readline()     
                    self.wfile.write(bytes(response, 'utf-8'))
                return
            elif self.path == '/actuator':
                # return the page that list all actuators...
                self.send_response(200) # OK
                self.send_header('Content-Type', 'text/html; charset=UTF-8')            
                self.end_headers()
                response = ''
                # read all lines of a html page and return it to browser...
                with open('public_html/actuator.html', 'r') as f:
                    line = f.readline()
                    while line:
                        response += line
                        line = f.readline()     
                    self.wfile.write(bytes(response, 'utf-8'))
                return
            elif self.path == '/sensor/list':
                # returns all sensors formatted as a JSON array
                self.send_response(200) # OK
                self.send_header('Content-Type', 'application/json; charset=UTF-8;')            
                self.end_headers()
                first = True
                self.wfile.write(bytes('[', 'utf-8'))
                for p in broker.get_publishers():
                    pub = broker.get_publishers()[p]
                    if first:
                        first = False
                    else:
                        self.wfile.write(bytes(',', 'utf-8'))
                    response = '{"id": %d, "status": "%s", "topic": "%s", "token": "%s", "data": "%s"}' %(pub['id'], pub['command'], pub['topic'], p, pub['data'])
                    self.wfile.write(bytes(response, 'utf-8'))
                self.wfile.write(bytes(']', 'utf-8'))
                return

            elif self.path == '/actuator/list':
                # returns all actuators formatted as a JSON array
                self.send_response(200) # OK
                self.send_header('Content-Type', 'application/json; charset=UTF-8')
                self.end_headers()
                first = True
                self.wfile.write(bytes('[', 'utf-8'))
                for g in broker.get_subscribers():
                    pub = broker.get_subscribers()[g]
                    if first:
                        first = False
                    else:
                        self.wfile.write(bytes(',', 'utf-8'))
                    response = '{"id": %d, "status": "%s", "topic": "%s", "token": "%s", "data": "%s"}' %(pub['id'], pub['command'], pub['topic'], g, pub['data'])
                    self.wfile.write(bytes(response, 'utf-8'))
                self.wfile.write(bytes(']', 'utf-8'))
                return
            elif self.path == '/actuator/state':
                # returns the actual state of an actuator
                length = int(self.headers['Content-Length'])
                request_data = self.rfile.read(length)
                request_data = request_data.decode('utf-8')
                json_data = json.loads(request_data)
                try:                    
                    p = broker.get_subscribers()[json_data['token']]
                    response = '{"command": "%s"}' %(p['command'])
                    self.wfile.write(bytes(response, 'utf-8'))
                    self.send_response(200)
                except Exception as e:
                    self.send_response(401) #Unauthorized
                return
            elif self.path == '/sensor/state':
                # returns the actual state of a sensor...
                length = int(self.headers['Content-Length'])
                request_data = self.rfile.read(length)
                request_data = request_data.decode('utf-8')
                json_data = json.loads(request_data)
                try:                    
                    p = broker.get_publishers()[json_data['token']]
                    self.send_response(200)
                    response = '{"command": "%s"}' %(p['command'])
                    self.wfile.write(bytes(response, 'utf-8'))
                    #self.send_header('Content-Type', 'application/json; charset=UTF-8')            
                    #self.end_headers()                    
                except Exception as e:
                    self.send_response(401) #Unauthorized
                return
            else:
                # Return the other types of files that a server can serve
                self.send_response(200) # OK           
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Content-Length', os.path.getsize('public_html'+self.path))
                f = open('public_html'+self.path, 'rb')
                name = os.path.relpath('public_html'+self.path)
                if name.endswith('.svg'):
                    self.send_header('Content-Type', 'image/svg+xml')
                else:
                    self.send_header('Content-Type', 'image/png')
                self.end_headers()
                line = f.read()
                while line:                    
                    self.wfile.write(line)
                    line = f.read()
                return

        def do_POST(self):
            split_path = self.path.split('/')
            if split_path[1] == 'sensor':
                handle_sensor_request(self, broker)
            elif split_path[1] == 'actuator':
                handle_actuator_request(self, broker)
        # genereate a token
        def generate_token(self):
            return str(secrets.token_hex(16))
    return Request_Handler