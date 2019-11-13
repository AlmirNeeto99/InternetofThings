from Server import Server

def main():
    s = Server('localhost', 8000)
    s.create_server()
    s.start()

main()