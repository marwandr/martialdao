import socket
import threading
import queue
from cultivator import Cultivator
import pickle
import gc
import random

def receive(data_queue, server, server_flag):  # All data received to the queue
    while server_flag:
        try:
            data, addr = server.recvfrom(2048)
            data_queue.put((data, addr))
        except:
            pass

def send(data_queue, clients, players, server, server_flag):     # Handle data
    global SPRITE_DATA
    while server_flag:
        while not data_queue.empty():
            # print(clients)
            data, addr = data_queue.get()
            if addr not in clients:
                if len(clients) > 2:
                    server.sendto("BUSY".encode(), addr)
                    continue
                if data.decode().startswith("CONNECT_REQ:"):
                    playerName = data.decode()[data.decode().index(":")+1:]
                    clients.append(addr)   
                    players[len(clients)-1].playerID = playerName
                    if len(clients) > 1:
                        if playerName == players[0].playerID:
                            server.sendto(f"ACCEPTED:{players[1].playerID}".encode(), addr)
                        elif playerName == players[1].playerID:
                            server.sendto(f"ACCEPTED:{players[0].playerID}".encode(), addr)
                else:
                    server.sendto("LOGIN-ERROR".encode(), addr)
                    continue
            else:
                for client in clients:
                    try:
                        if client != addr:
                            try:
                                if data.decode().startswith("FIGHTER-") or data.decode().startswith("CONNECT_REQ:"):
                                    pass
                                else:
                                    server.sendto(data, client)
                            except:
                                server.sendto(data, client)
                        else:
                            try:
                                if data.decode().startswith("FIGHTER-"):
                                    # print("Currently sending fighters")
                                    requestedFighter = data.decode()[data.decode().index("-")+1:]
                                    if players[0].playerID == requestedFighter:
                                        # print(f"Sending fighter {players[0]}")
                                        server.sendto(pickle.dumps(players[0]), client)
                                    elif players[1].playerID == requestedFighter:
                                        # print(f"Sending fighter {players[1]}")
                                        server.sendto(pickle.dumps(players[1]), client)
                                    else:
                                        # print("Oops, no fighter to be sent, wrong ID..")
                                        server.sendto("WRONG-ID".encode(), client)
                                elif data.decode().startswith("CONNECT_REQ:"):
                                    playerName = data.decode()[data.decode().index(":")+1:]
                                    if len(clients) > 1:
                                        server.sendto(f"ACCEPTED:{playerName}".encode(), addr)
                            except:
                                pass
                    except:
                        clients.remove(client)
                        print("Opponent disconnected")

def start_server(serverqueue, server_flag):
    global SPRITE_DATA
    gc.enable()

    # Sprite variables
    SPRITE_SIZE = 162
    SPRITE_SCALE = 4
    SPRITE_OFFSET = [72, 56]
    SPRITE_DATA = [SPRITE_SIZE, SPRITE_SCALE, SPRITE_OFFSET]

    data_queue = queue.Queue()
    clients = []
    players = [Cultivator(200, 310, False, SPRITE_DATA, None, False), # Player 1
                Cultivator(700, 310, True, SPRITE_DATA, None, True)] # Player 2
    
    while True:
        try:
            server_address = '127.0.0.1'
            server_port = random.randint(8000, 9000)

            server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server.bind((server_address, server_port))
            break
        except:
            server_port = random.randint(8000, 9000)
            continue

    serverqueue.put(server_address)
    serverqueue.put(server_port)

    t1 = threading.Thread(target=receive, args=(data_queue, server,server,))
    t2 = threading.Thread(target=send, args=(data_queue, clients, players, server,server_flag,))

    t1.start()
    t2.start()
