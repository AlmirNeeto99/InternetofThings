from Client import Client

class Subscriber(Client):
    def __init__(self, host, port, topics):
        super().__init__()

    def receive(self):
        pass
