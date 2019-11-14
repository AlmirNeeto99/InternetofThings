from Client import Client
from HTTP_Request import format_request
import json

class Subscriber(Client):
    def __init__(self, host, port, topics):
        super().__init__()
        self.token = 0
        self.host = host
        self.port = port
        self.topic = topics

    def subscribe_subscriber(self):
        data = '{"method": "subscribe", "topic": "%s"}' %(self.topic)
        self.client.send(bytes(format_request(method='POST', path='/actuator', data=data, content_type='application/json'), 'utf-8'))
        response = self.client.recv(1024)
        response = response.decode('utf-8')
        self.token = response

    def receive(self):
        self.connect(self.host, self.port)
        #if self.token == 0:
            #self.subscribe_subscriber()
        sent_data = {}
        sent_data['topic'] = self.topic
        sent_data['token'] = self.token
        sent_data['method'] = 'publish'
        data = json.dumps(sent_data)
        self.client.send(bytes(format_request(method='GET', path='/sensor', data=data, content_type='application/json'), 'utf-8'))
        response = self.client.recv(1024)
        self.client.close()
        return response