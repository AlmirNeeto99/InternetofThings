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
    # Subscribe a publisher to the server.
    def subscribe_publisher(self, topic):
        self.connect(self.host, self.port)
        data = '{"topic": "%s"}' % (topic)
        self.client.send(bytes(format_request(method='POST', path='/sensor/subscribe',
                                              data=data, content_type='application/json'), 'utf-8'))
        response = self.client.recv(1024)
        response = response.decode('utf-8')
        response = json.loads(response)
        self.token = response['token']
        self.client.close()
    # Send a message to the server...
    def publish(self, sent_data):
        self.connect(self.host, self.port)
        sent_data['topic'] = self.topic
        sent_data['token'] = self.token
        data = json.dumps(sent_data)
        self.client.send(bytes(format_request(method='POST', path='/sensor/publish',
                                              data=data, content_type='application/json'), 'utf-8'))
        response = self.client.recv(1024)
        response = response.decode('utf-8')
        response = json.loads(response)
        command = response['command']
        self.client.close()
        return command
    # Check the server if publisher stats has changed...
    def get_status(self):
        self.connect(self.host, self.port)
        send = {"token": self.token}
        send = json.dumps(send)
        self.client.send(bytes(format_request(method='GET', path='/sensor/state',
                                              data=send, content_type='application/json'), 'utf-8'))
        response = self.client.recv(1024)
        response = response.decode('utf-8')
        response = json.loads(response)
        status = response['command']
        self.client.close()
        return status
    # Tells the server this publisher will stop sending messages
    def stop_sending(self):
        self.connect(self.host, self.port)
        send = {"token": self.token, "action": "stop"}
        send = json.dumps(send)
        self.client.send(bytes(format_request(method='POST', path='/sensor/config/device',
                                              data=send, content_type='application/json'), 'utf-8'))
        response = self.client.recv(1024)
        response = response.decode('utf-8')
        response = json.loads(response)
        status = response['status']
        self.client.close()
        return status
    # Tells the server this publisher will start sending messages
    def start_sending(self):
        self.connect(self.host, self.port)
        send = {"token": self.token, "action": "start"}
        send = json.dumps(send)
        self.client.send(bytes(format_request(method='POST', path='/sensor/config/device',
                                              data=send, content_type='application/json'), 'utf-8'))
        response = self.client.recv(1024)
        response = response.decode('utf-8')
        response = json.loads(response)
        status = response['status']
        self.client.close()
        return status