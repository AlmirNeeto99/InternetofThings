from Client import Client
from HTTP_Request import format_request
import time
import json


class Publisher(Client):

    def __init__(self, topic, host, port):
        self.topic = topic
        self.host = host
        self.port = port

    def publish(self, sentData):                
        while True:
            self.connect(self.host, self.port)
            sentData['topic'] = self.topic
            data = json.dumps(sentData)
            self.client.send(bytes(format_request(method='PUT', path='/sensor', data=data, content_type='application/json'), 'utf-8'))
            self.client.close()
            time.sleep(5)