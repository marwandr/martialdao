import socket
import threading
import queue
from cultivator import Cultivator
import pickle

# Sprite variables
DREAMER_ANIMATION_FRAMES = [10, 8, 1, 7, 7, 3, 7]
SPRITE_SIZE = 162
SPRITE_SCALE = 4
SPRITE_OFFSET = [72, 56]
SPRITE_DATA = [SPRITE_SIZE, SPRITE_SCALE, SPRITE_OFFSET]

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 8000

data_queue = queue.Queue()
clients = []
players = [Cultivator(200, 310, False, SPRITE_DATA, None), # Player 1
            Cultivator(700, 310, True, SPRITE_DATA, None)] # Player 2

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP socket
server.bind((SERVER_ADDRESS, SERVER_PORT))

def receive():  # All data received to the queue
    while True:
        try:
            data, addr = server.recvfrom(2048)
            data_queue.put((data, addr))
        except:
            pass

def send():     # Handle data
    while True:
        while not data_queue.empty():
            data, addr = data_queue.get()
            if addr not in clients:
                if len(clients) > 2:
                    server.sendto("BUSY".encode(), addr)
                    continue
                else:
                    if data.decode().startswith("CONNECT_REQ:"):
                        print(f"Connected: {addr}")
                        clients.append(addr)
                        playerName = data.decode()[data.decode().index(":")+1:]
                        players[len(clients)-1].playerID = playerName
                    else:
                        server.sendto("LOGIN-ERROR".encode(), addr)
                        continue
            for client in clients:
                try:
                    if client != addr:
                        try:
                            if data.decode().startswith("FIGHTER-"):
                                pass
                            else:
                                server.sendto(data, client)
                        except:
                            server.sendto(data, client)
                    if client == addr:
                        try:
                            if data.decode().startswith("FIGHTER-"):
                                print("Currently sending fighters")
                                requestedFighter = data.decode()[data.decode().index("-")+1:]
                                if players[0].playerID == requestedFighter:
                                    print(f"Sending fighter {players[0]}")
                                    server.sendto(pickle.dumps(players[0]), client)
                                elif players[1].playerID == requestedFighter:
                                    print(f"Sending fighter {players[1]}")
                                    server.sendto(pickle.dumps(players[1]), client)
                                else:
                                    print("Oops, no fighter to be sent, wrong ID..")
                                    server.sendto("WRONG-ID".encode(), client)
                        except:
                            pass
                    else:
                        pass
                except:
                    clients.remove(client)

t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=send)

t1.start()
t2.start()
