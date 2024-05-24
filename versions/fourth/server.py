import socket
import threading
import queue
from cultivator import Cultivator
import pickle
import gc
import random

def anticheat(check, sample):
    global cheat
    ### If the difference in health is bigger than 30 there was manipulation in health
    if check.health - sample.health > 30 or sample.health - check.health > 30:
            print(f"{sample.playerID} caught with suspicious HP manipulation!")
            print(f"HP went from {sample.health} to {check.health}")
            cheat = True
    elif check.pos.x -sample.pos.x > 20 or sample.pos.x - check.pos.x > 20:
            print(f"{sample.playerID} caught with suspicious x-movement manipulation!")
            print(f"X position went from {sample.pos.x} to {check.pos.x}")
            cheat = True
    elif (check.pos.y - sample.pos.y) > 30 or (sample.pos.y - check.pos.y) > 30:
            print(f"{sample.playerID} caught with suspicious y-movement manipulation!")
            print(f"Y position went from {sample.pos.y} to {check.pos.y}")
            cheat = True

def receive(data_queue, server):  # All data received to the queue
    while True:
        try:
            data, addr = server.recvfrom(2048)
            data_queue.put((data, addr))
        except:
            pass

def send(data_queue, clients, players, server,cheat_queue):     # Handle data
    global SPRITE_DATA
    global cheat
    ### Dictionaries used for anti cheating, we will compare the before and after
    ### For each player to check for package manipulation
    # before = {}
    while True:
        while not data_queue.empty():
            # print(clients)
            data, addr = data_queue.get()
            if addr not in clients:
                if len(clients) > 2:
                    server.sendto("BUSY".encode(), addr)
                    continue
                if data.decode().startswith("CONNECT_REQ"):
                    playerName = data.decode()[data.decode().index(":")+1:]
                    clients.append(addr)   
                    if data.decode().startswith("CONNECT_REQ1"):
                        players[1].playerID = playerName
                    else:
                        players[0].playerID = playerName
                    # for i in range(0, len(players)-1):
                    #     print(players[i].playerID)
                    if len(clients) > 1:
                        if playerName is players[0].playerID:
                            server.sendto(f"ACCEPTED:{players[1].playerID}".encode(), addr)
                            # before[addr] = players[0]
                            # print(f"{addr} player1")
                        elif playerName is players[1].playerID:
                            server.sendto(f"ACCEPTED:{players[0].playerID}".encode(), addr)
                            # before[addr] = players[1]
                            # print(f"{addr} player2")
                else:
                    server.sendto("LOGIN-ERROR".encode(), addr)
                    continue
            else:
                for client in clients:
                    try:
                        if client != addr:
                            try:
                                if data.decode().startswith("FIGHTER-") or data.decode().startswith("CONNECT_REQ"):
                                    pass
                                else:
                                    server.sendto(data, client)
                            ### Sending the player objects, first checking for anti-cheat
                            except:
                                # check = pickle.loads(data)
                                # sample = before[addr]
                                # ch_thr = threading.Thread(target=anticheat, args=(check, sample,))
                                # ch_thr.start()
                                # before[addr] = check
                                # print(f"sending fighter {pickle.loads(data)} to {client}")
                                server.sendto(data, client)
                        else:
                            try:
                                if data.decode().startswith("FIGHTER-"):
                                    # print("Currently sending fighters")
                                    requestedFighter = data.decode()[data.decode().index("-")+1:]
                                    # print(f"server requested fighter; {requestedFighter}, by {addr}")
                                    if players[0].playerID == requestedFighter:
                                        # print(f"Sending fighter {players[0]}")
                                        server.sendto(pickle.dumps(players[0]), client)
                                        # print("sending fighter 1")
                                    elif players[1].playerID == requestedFighter:
                                        # print(f"Sending fighter {players[1]}")
                                        server.sendto(pickle.dumps(players[1]), client)
                                        # print("sending fighter 2")
                                    else:
                                        # print("Oops, no fighter to be sent, wrong ID..")
                                        server.sendto("WRONG-ID".encode(), client)
                                elif data.decode().startswith("CONNECT_REQ"):
                                    playerName = data.decode()[data.decode().index(":")+1:]
                                    # print(playerName)
                                    if len(clients) > 1:
                                        server.sendto(f"ACCEPTED:{playerName.playerID}".encode(), addr)
                            except:
                                # print(f"Passing {clients}")
                                pass
                    except Exception as e:
                        print(f"Something went wrong, {e}")
                        clients.remove(client)

def start_server(serverqueue):
    global SPRITE_DATA
    global cheat
    cheat = False
    gc.enable()

    # Sprite variables
    SPRITE_SIZE = 162
    SPRITE_SCALE = 4
    SPRITE_OFFSET = [72, 56]
    SPRITE_DATA = [SPRITE_SIZE, SPRITE_SCALE, SPRITE_OFFSET]

    data_queue = queue.Queue()
    cheat_queue = queue.Queue
    clients = []
    players = [Cultivator(200, 310, False, SPRITE_DATA, None, False), # Player 1
                Cultivator(700, 310, True, SPRITE_DATA, None, True)] # Player 2
    
    server_address = '127.0.0.1'
    server_port = random.randint(8000, 9000)

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((server_address, server_port))

    serverqueue.put(server_address)
    serverqueue.put(server_port)

    t1 = threading.Thread(target=receive, args=(data_queue, server,))
    t2 = threading.Thread(target=send, args=(data_queue, clients, players, server,cheat_queue,))

    t1.start()
    t2.start()
