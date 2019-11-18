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

    def subscribe_publisher(self, topic):
        self.connect(self.host, self.port)
        data = '{"topic": \"%s\"}' % (topic)
        self.client.send(bytes(format_request(method='POST', path='/sensor/subscribe',
                                              data=data, content_type='application/json'), 'utf-8'))
        response = self.client.recv(1024)
        response = response.decode('utf-8')
        self.token = response
        self.client.close()

    def publish(self, sent_data):
        self.connect(self.host, self.port)
        sent_data['topic'] = self.topic
        sent_data['token'] = self.token
        data = json.dumps(sent_data)
        self.client.send(bytes(format_request(method='POST', path='/sensor/publish',
                                              data=data, content_type='application/json'), 'utf-8'))
        self.client.close()
