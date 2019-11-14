import Subscriber, Publisher

class Broker():
    def __init__(self):
        self.subscribers = {}
        self.publishers = list()

    def get_subscribers(self):
        return self.subscribers

    def get_publishers(self):
        return self.publishers