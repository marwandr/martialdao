import socket
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket
        self.HOST = ('127.0.0.1', 8000)
        self.player = self.connect()

    def get_player(self):
        return self.player

    def end_connection(self):
        self.client.close()

    def connect(self):
        try:
            self.client.sendto("Connection".encode("utf-8"), self.HOST)
            received_data, addr = self.client.recvfrom(2048)
            if received_data == b"BUSY\n":
                return "BUSY\n"
            elif received_data == b"ALREADY-CONNECTED\n":
                return"ALREADY-CONNECTED\n"
            elif received_data == b"NOT-IN-MATCH\n":
                return "NOT-IN-MATCH\n"
            else:
                return pickle.loads(received_data)
        except socket.error as e:
            print("Connection error:", e)
            return None

    def send(self, data):
        try:
            self.client.sendto(pickle.dumps(data), self.HOST)
            received_data, addr = self.client.recvfrom(2048)
            if received_data == b"Time-out":
                return "Time-out"
            else:
                return pickle.loads(received_data)
        except socket.error as e:
            print("Send error:", e)
            return None
