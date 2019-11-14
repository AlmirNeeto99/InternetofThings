from Client import Client
from HTTP_Request import format_request
import json

class Publisher(Client):
    def __init__(self, topic, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.topic = topic
        self.token = 0

    def subscribe_publisher(self):
        data = '{"method": "subscribe"}'
        self.client.send(bytes(format_request(method='POST', path='/sensor', data=data, content_type='application/json'), 'utf-8'))
        response = self.client.recv(1024)
        response = response.decode('utf-8')
        self.token = response

    def publish(self, sent_data):
        self.connect(self.host, self.port)
        if self.token == 0:                    
            self.subscribe_publisher()
        sent_data['topic'] = self.topic
        sent_data['token'] = self.token
        sent_data['method'] = 'publish'
        data = json.dumps(sent_data)
        self.client.send(bytes(format_request(method='POST', path='/sensor', data=data, content_type='application/json'), 'utf-8'))
        self.client.close()