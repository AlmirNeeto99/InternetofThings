from http.server import HTTPServer, BaseHTTPRequestHandler
from Sensor_Handler import handle_sensor_request
from Actuator_Handler import handle_actuator_request
import os, threading, json, secrets

def handle_request(broker):
    class Request_Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            split_path = self.path.split('/')
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
            elif self.path == '/sensor':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=UTF-8')            
                self.end_headers()
                if len(broker.get_publishers()) == 0:
                    self.wfile.write(bytes('{"status": "No sensors found"}', 'utf-8'))
                else:
                    first = True
                    self.wfile.write(bytes('{"sensors": [', 'utf-8'))
                    for p in broker.get_publishers():
                        if first:
                          first = False
                        else:
                          self.wfile.write(bytes(',', 'utf-8'))
                        self.wfile.write(bytes('{"token": "'+p['token'] + '"}', 'utf-8'))
                    self.wfile.write(bytes(']}', 'utf-8'))
            elif self.path == '/actuator':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=UTF-8')            
                self.end_headers()
                if len(broker.get_subscribers()) == 0:
                    self.wfile.write(bytes('{"status": "No sensors found"}', 'utf-8'))
                else:
                    first = True
                    self.wfile.write(bytes('{"actuators": [', 'utf-8'))
                    for g in broker.get_subscribers():
                        if first:
                          first = False
                        else:
                          self.wfile.write(bytes(',', 'utf-8'))
                        self.wfile.write(bytes('{"token": "' + g['token'] + '"}', 'utf-8'))
                    self.wfile.write(bytes(']}', 'utf-8'))
            else:
                #self.send_response(404)
                #self.end_headers()
                #return
                self.send_response(200)                
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