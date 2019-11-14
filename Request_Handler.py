from http.server import HTTPServer, BaseHTTPRequestHandler
import os, threading, json, secrets

def handle_request(broker):
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
            if self.path == '/sensor':
                length = int(self.headers['Content-Length'])
                request_data = self.rfile.read(length)
                request_data = request_data.decode('utf-8')
                json_data = json.loads(request_data)
                if json_data['method'] == 'subscribe':
                    pubs = broker.get_publishers()
                    token = self.generate_token()
                    if token not in pubs:
                        pubs.append(token)
                    else:
                        token = self.generate_token()
                        while token in pubs:
                            token = self.generate_token()
                        pubs.append(token)
                    self.wfile.write(bytes(token, 'utf-8'))
                elif json_data['method'] == 'publish':
                    if json_data['token'] in broker.get_publishers():
                        topic = json_data['topic']
                        subscribed_clients = broker.get_subscribers()
                        subscribed_clients[topic] = json_data['message']
                        print(subscribed_clients)
                        self.send_response(200)
                    else:
                        self.send_response(400)

        def generate_token(self):
            return str(secrets.token_hex(16))
    return Request_Handler