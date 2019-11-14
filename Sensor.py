from Publisher import Publisher
import random, time


class Sensor(Publisher):
    def __init__(self, topic, host, port):
        super().__init__(topic, host, port)

    def send_data(self):
        data = {}        
        while True:
            data['message'] = self.generate_data()
            self.publish(data)
            time.sleep(5)

    def generate_data(self):
        return random.randint(20, 40)

def main():
    s = Sensor('fsa', 'localhost', 8000)
    s.send_data()

main()