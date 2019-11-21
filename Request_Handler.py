from http.server import HTTPServer, BaseHTTPRequestHandler
from Sensor_Handler import handle_sensor_request
from Actuator_Handler import handle_actuator_request
import os, threading, json, secrets

def handle_request(broker):
    class Request_Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            split_path = self.path.split('/')
            print(split_path)
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
                self.send_header('Content-Type', 'text/html; charset=UTF-8')            
                self.end_headers()
                if len(broker.get_publishers()) == 0:
                    self.wfile.write(bytes('No sensors found', 'utf-8'))
                else:
                    for p in broker.get_publishers():
                        print(p)
                        self.wfile.write(bytes(p['token'] + '\n', 'utf-8'))
            elif self.path == '/actuator':
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=UTF-8')            
                self.end_headers()
                if len(broker.get_subscribers()) == 0:
                    self.wfile.write(bytes('No sensors found', 'utf-8'))
                else:
                    for g in broker.get_subscribers():
                        self.wfile.write(bytes(g['token'] + '\n', 'utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                return
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
            print(split_path)

        def generate_token(self):
            return str(secrets.token_hex(16))
    return Request_Handler