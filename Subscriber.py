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
        # Subscribe an actuator to a server
        self.connect(self.host, self.port)
        data = '{"topic": "%s"}' %(self.topic)
        self.client.send(bytes(format_request(method='POST', path='/actuator/subscribe', data=data, content_type='application/json'), 'utf-8'))
        response = self.client.recv(1024)
        response = response.decode('utf-8')
        response = json.loads(response)
        self.token = response['token']
        self.client.close()
    # Read a message from server
    def receive(self):
        self.connect(self.host, self.port)
        sent_data = {}
        sent_data['topic'] = self.topic
        sent_data['token'] = self.token
        data = json.dumps(sent_data)
        self.client.send(bytes(format_request(method='POST', path='/actuator/receive', data=data, content_type='application/json'), 'utf-8'))
        response = self.client.recv(1024)
        self.client.close()
        return response
    # Get the actual status of the device
    def get_status(self):
        self.connect(self.host, self.port)
        send = {"token": self.token}
        send = json.dumps(send)
        self.client.send(bytes(format_request(method='GET', path='/actuator/state',
                                              data=send, content_type='application/json'), 'utf-8'))
        response = self.client.recv(1024)
        response = response.decode('utf-8')
        response = json.loads(response)
        status = response['command']
        self.client.close()
        return status
    # Tells the server this subscriber will start reading messages
    def start_receiving(self):
        self.connect(self.host, self.port)
        send = {"token": self.token, "action": "start"}
        send = json.dumps(send)
        self.client.send(bytes(format_request(method='POST', path='/actuator/config/device',
                                              data=send, content_type='application/json'), 'utf-8'))
        response = self.client.recv(1024)
        response = response.decode('utf-8')
        response = json.loads(response)
        status = response['status']
        self.client.close()
        return status
    # Tells the server this subscriber will stop reading messages
    def stop_receiving(self):
        self.connect(self.host, self.port)
        send = {"token": self.token, "action": "stop"}
        send = json.dumps(send)
        self.client.send(bytes(format_request(method='POST', path='/actuator/config/device',
                                              data=send, content_type='application/json'), 'utf-8'))
        response = self.client.recv(1024)
        response = response.decode('utf-8')
        response = json.loads(response)
        status = response['status']
        self.client.close()
        return status