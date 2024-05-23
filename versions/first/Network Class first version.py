import socket

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER_ADDRESS = '127.0.0.1'
        self.SERVER_PORT = 8000
        self.pos = self.connect()

    def get_pos(self):
        return self.pos

    def connect(self):
        try:
            self.client.connect((self.SERVER_ADDRESS, self.SERVER_PORT))
            return self.client.recv(2048).decode()
        except:
            pass
        
    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return self.client.recv(2048).decode()
        except socket.error as e:
            print(e)
            