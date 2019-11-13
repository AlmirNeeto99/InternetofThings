import socket
class Client():
    def connect(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
        self.client.connect((host, port))

    def close(self):
        self.client.close()
