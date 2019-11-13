from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
from Request_Handler import Request_Handler as handler
from Broker import Broker
    
class Rest:
    def __init__(self):
        self.broker = Broker()
    
    def start(self):
        httpd = HTTPServer(('localhost', 8000), handler)
        print('-> Server listening to localhost:8000')
        httpd.serve_forever()


def main():
    server = Rest()
    server.start()

main()