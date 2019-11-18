import Subscriber
import Publisher


class Broker():
    id = 1  # auxiliar variable just to track created clients

    def __init__(self):
        self.subscribers = list()
        self.publishers = list()
        self.published_messages = {}

    def get_subscribers(self):
        return self.subscribers

    def get_publishers(self):
        return self.publishers

    def get_published_messages(self):
        return self.published_messages
