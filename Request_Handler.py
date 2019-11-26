from http.server import HTTPServer, BaseHTTPRequestHandler
from Sensor_Handler import handle_sensor_request
from Actuator_Handler import handle_actuator_request
import os, threading, json, secrets

def handle_request(broker):
    class Request_Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            split_path = self.path.split('/')
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
            elif self.path == '/sensor':
                self.send_response(200) # OK
                self.send_header('Content-Type', 'text/html; charset=UTF-8')            
                self.end_headers()
                response = ''
                with open('public_html/sensor.html', 'r') as f:
                    line = f.readline()
                    while line:
                        response += line
                        line = f.readline()     
                    self.wfile.write(bytes(response, 'utf-8'))
            elif self.path == '/actuator':
                self.send_response(200) # OK
                self.send_header('Content-Type', 'text/html; charset=UTF-8')            
                self.end_headers()
                response = ''
                with open('public_html/actuator.html', 'r') as f:
                    line = f.readline()
                    while line:
                        response += line
                        line = f.readline()     
                    self.wfile.write(bytes(response, 'utf-8'))
            elif self.path == '/sensor/list':
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
                    response = '{"id": %d, "status": "%s", "topic": "%s", "token": "%s"}' %(pub['id'], pub['status'], pub['topic'], p)                    
                    self.wfile.write(bytes(response, 'utf-8'))
                self.wfile.write(bytes(']', 'utf-8'))
            elif self.path == '/actuator/list':
                self.send_response(200) # OK
                self.send_header('Content-Type', 'application/json; charset=UTF-8')            
                self.end_headers()
                first = True
                self.wfile.write(bytes('[', 'utf-8'))
                for g in broker.get_subscribers():
                    if first:
                        first = False
                    else:
                        self.wfile.write(bytes(',', 'utf-8'))
                    self.wfile.write(bytes('{"token": "' + g['token'] + '"}', 'utf-8'))
                self.wfile.write(bytes(']', 'utf-8'))
            elif self.path == '/sensor/state':
                length = int(self.headers['Content-Length'])
                request_data = self.rfile.read(length)
                request_data = request_data.decode('utf-8')
                json_data = json.loads(request_data)
                try:
                    p = broker.get_publishers()[json_data['token']]
                    response = '{"command": "%s"}' %(p['command'])
                    print(response)
                    self.wfile.write(bytes(response, 'utf-8'))
                    self.send_header('Content-Type', 'application/json; charset=UTF-8')            
                    self.end_headers()
                    self.send_response(200)
                except Exception as e:
                    self.send_response(401) #Unauthorized
            else:
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

        def do_POST(self):
            split_path = self.path.split('/')
            if split_path[1] == 'sensor':
                handle_sensor_request(self, broker)
            elif split_path[1] == 'actuator':
                handle_actuator_request(self, broker)

        def generate_token(self):
            return str(secrets.token_hex(16))
    return Request_Handler