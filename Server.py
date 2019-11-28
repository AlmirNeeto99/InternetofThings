from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import Request_Handler as handler
from Broker import Broker
    
class Rest:
    def __init__(self):
        self.broker = Broker() # Create a broker
    
    def start(self):
        request_handler = handler.handle_request(self.broker)
        httpd = HTTPServer(('localhost', 8000), request_handler)
        print('-> Server listening...')
        httpd.serve_forever()

def main():
    server = Rest()
    server.start()

main()