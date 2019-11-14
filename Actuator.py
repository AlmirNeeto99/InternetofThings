from Subscriber import Subscriber
import time


class Actuator(Subscriber):
    def __init__(self, topic, host, port):
        super().__init__(host, port, topic)

    def read_data(self):    
        while True:
            print(self.receive().decode('utf-8'))
            time.sleep(5)

def main():
    s = Actuator('fsa', 'localhost', 8000)
    s.read_data()

main()