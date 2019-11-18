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
                length = int(self.headers['Content-Length'])
                request_data = self.rfile.read(length)
                request_data = request_data.decode('utf-8')
                json_data = json.loads(request_data)
                print(json_data)
                self.send_response(200)
                data = broker.get_subscribers()[json_data['topic']]
                print(data)
                self.wfile.write(bytes(str(data), 'utf-8'))
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'image/png')
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Content-Length', os.path.getsize('public_html'+self.path))
                self.end_headers()
                with open('public_html'+self.path, 'rb') as f:
                    self.wfile.write(f.read())

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