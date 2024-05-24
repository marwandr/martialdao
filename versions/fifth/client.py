# With help from: https://www.youtube.com/watch?v=s5bd9KMSSW4

import socket
import threading
import random
import pickle
import pygame
import queue
from server import *
from cultivator import Cultivator
from pygame import mixer
import pyfiglet
import gc
import os
import subprocess
import re
import platform

gc.enable()

opponent_name = None
start_game = False
network_flag = True
lost_conn = False
    
def get_ip():
    os_system = platform.system()
    if os_system == "Windows":
        command = subprocess.run(['ipconfig'], capture_output=True, text=True)
    elif os_system == "Linux":
        command = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
    elif os_system == "Darwin":
        command = subprocess.run(['ifconfig'], capture_output=True, text=True)
    else:
        print(f"Unsupported OS: {os_system}")
        return 1
    
    if command.returncode != 0:
        print("Failed to retrieve IP address")
        return 1
    output = command.stdout
    if os_system == "Windows":
        ipv4 = re.compile(r'IPV4 Address[. ]*: (\d+\.\d+\.\d+\.\d+)')
    elif os_system == "Linux":
        ipv4 = re.compile(r'inet (\d+\.\d+\.\d+\.\d+)/\d+')
    else:
        ipv4 = re.compile(r'inet (?:addr:)?(\d+\.\d+\.\d+\.\d+)')

    address = ipv4.findall(output)
    if address:
        return address[0]
    else:
        return 1

def get_player(ID, client):
    global host_address
    global host_port
    client.sendto(f"FIGHTER-{ID}".encode(), (host_address, host_port))
    data, _ = client.recvfrom(2048)
    try:
        # print(pickle.loads(data))
        if pickle.loads(data) == None:
            return get_player(ID, client)
        return pickle.loads(data)
    except:
        if data.decode() == "WRONG-ID":
            print("Something went wrong while requesting player information, please try again.")
            print(data.decode())
            client.close()
            return "error"
        elif "ACCEPTED" in data.decode():
            return get_player(ID, client)
        elif "RESET-SUCCESS" in data.decode():
            return get_player(ID, client)
        else:
            print("Something went wrong while requesting player information, please try again.")
            print(data.decode())
            client.close()
            return "error"
    
def send_player(player, client):
    global host_address
    global host_port
    client.sendto(pickle.dumps(player), (host_address, host_port))
    # print("Receiving")
    data, _ = client.recvfrom(2048)
    # print("Received")
    try:
        # print(pickle.loads(data))
        if pickle.loads(data) is None:
            return send_player(player)
        return pickle.loads(data)
    except:
        if data.decode() == "WRONG-ID":
            print("Something went wrong while requesting player information, please try again.")
            client.close()
            return "error"

def receive(client):
    global receive_thread
    global opponent_name
    global start_game
    while receive_thread:
        try:
            data, _ = client.recvfrom(2048)
            if "ACCEPTED" in data.decode():
                # print(data.decode())
                opponent_name = data.decode()[data.decode().index(":")+1:]
                receive_thread = False
                start_game = True
                break
            elif data.decode() == "REJECTED":
                print("Sadly, the opponent was not brave enough to accept your challenge.")
                client.close()
                opponent_name = "error"
                receive_thread = False
            elif data.decode() == "BUSY":
                print("The server is too busy currently. Try to join another time :)")
                client.close()
                opponent_name = "error"
                receive_thread = False
            elif data.decode() == "LOGIN-ERROR":
                print("This file has been corrupted, please reinstall.")
                client.close()
                opponent_name = "error"
                receive_thread = False        
            else:
                print("Something has gone wrong. Please try again.")
                print(data.decode())
                client.close()
                opponent_name = "error"
                receive_thread = False
        except:
            pass

def menu():
    head = pyfiglet.figlet_format("MARTIAL DAO", font="slant")
    head2 = pyfiglet.figlet_format("Created by Marwan Amrhar", font="mini")
    print(head)
    print(head2)

def start(client):
    global host_address
    global host_port
    global name
    global opponent_name
    global serverqueue
    global receive_thread
    global server_flag
    os.system("clear")
    menu()
    opt1 = pyfiglet.figlet_format("[1] Local mode", font="digital")
    opt2 = pyfiglet.figlet_format("[2] Online mode", font="digital")
    print(opt1)
    print(opt2)
    while True:
        option = input()
        if option != "1" and option != "2":
            print("Please enter either 1 or 2.")
        else:
            break
    if option == "1":
        local = True
        server_address = '127.0.0.1'
        server_port = random.randint(8000, 9000)
    else:
        local = False
        server_address = get_ip()
        if server_address == 1:
            print("Couldn't retrieve IP address! Entering local game mode...")
            server_address = '127.0.0.1'
            local = True
        server_port = random.randint(8000, 9000)        

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.bind((server_address, server_port))

    os.system("clear")
    menu()
    menuname= pyfiglet.figlet_format("Enter your nickname", font="digital")
    print(menuname)
    name = input()
    opponent_name = None
    serverqueue = queue.Queue()

    os.system("clear")
    menu()
    print("------------------------------")
    print("| Do you want to host? (y/n) | ")
    print("------------------------------")
    while True:
        host = input()
        if host == "y":
            host = True
        elif host == "n":
            host = False
        else:
            print("Please enter y or n.")
            continue
        if host:
            server_flag = True
            s = threading.Thread(target=start_server,args=(serverqueue,server_flag))
            s.start()
            host_address = serverqueue.get(True)
            host_port = serverqueue.get(True)
            os.system("clear")
            menu()
            print("----------------------------------")
            if local is False:
                print(f"| Server address: {host_address}      |")
            print(f"| Server port: {host_port}              |")
            print("----------------------------------")
            print("Waiting for opponent...")
            break
        else:
            if local is False:
                host_address = input("What is the address of the host you want to join?\n")
                if host_address == "local":
                    host_address = '127.0.0.1'
            else:
                host_address = '127.0.0.1'
            try:
                host_port = int(input("What is the port?\n"))
                print("Connecting...")
            except:
                print("Invalid host port...")
                continue
            break

    receive_thread = True
    t = threading.Thread(target=receive, args=(client,))
    t.start()
    while not start_game:
        client.sendto(f"CONNECT_REQ:{name}".encode(), (host_address, host_port))
    print("------------------------------------------------")
    print("| Opponent connected. Commencing battlefield... |")
    print("------------------------------------------------")
    t.join()
    if opponent_name == "error":
        print("Exiting...")
        client.close()
    else:
        game(opponent_name, client)
        exit(0)


#################--MAIN GAME--###############################################################

# Colors
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Sprite variables
SPRITE_SIZE = 162
SPRITE_SCALE = 4
SPRITE_OFFSET = [72, 56]

### Function for resetting
def reset(fighter_1):
    try:
        if fighter_1.opp == True:
            fighter_1.pos = pygame.Rect((700, 310, 80, 180))
            fighter_1.flip = True
        else:
            fighter_1.pos = pygame.Rect((200, 310, 80, 180))
            fighter_1.flip = False
        fighter_1.health = 100
        fighter_1.alive = True
        return 0
    except:
        return 1

# Function for sending & receiving data thread
def networking(fighter_1, client):
    # global network_flag
    global fighter_2
    global lost_conn
    while network_flag:
        try:
            fighter_2 = send_player(fighter_1, client)
        except Exception as e:
            print(f"Exception in networking: {e}")
            lost_conn = True
            break

# Function for quitting game thread
def quit_game(client):
    global run
    global network_flag
    global server_flag
    while network_flag:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Closing connection with server")
                    network_flag = False
                    run = False
                    server_flag = False
                    client.close()
                    pygame.quit()
                    exit()
        except:
            pass

# Drawing health bars
def draw_health_bar(health, x, y, screen):
    ratio = health / 100
    pygame.draw.rect(screen, BLACK, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))

# Writing text
def writeText(text, font, text_color, x, y, screen):
        img = font.render(text, True, text_color)
        screen.blit(img, (x, y))

# Load the images and return a list
def loadImages(spritesheetsrc, animationSteps):
    spritesheet = pygame.image.load(spritesheetsrc).convert_alpha()
    animationList = []
    for y, animation in enumerate(animationSteps):
        temp_img_list = []
        for steps in range(animation):
            temp_img = spritesheet.subsurface(steps * SPRITE_SIZE, y * SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE)
            temp_img_list.append(pygame.transform.scale(temp_img, (SPRITE_SIZE * SPRITE_SCALE, SPRITE_SIZE * SPRITE_SCALE)))
        animationList.append(temp_img_list)
    return animationList

# Main game func
def game(opponentName, client):
    global name
    global receive_thread
    global fighter_2
    global network_flag
    global lost_conn
    global server_flag
    ### Stop thread for receiving
    receive_thread = False
    try:
        pygame.init()
        mixer.init()
        ### Start quit & networking threads again every new game, and draw assets
        print("Creating game window...")

        ### Create the game window
        SCREEN_WIDTH = 1000
        SCREEN_HEIGHT = 600

        screen = pygame.display.set_mode((500, 500))
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Martial Dao")

        ### Set framerate
        clock = pygame.time.Clock()
        FPS = 60

        ### Game variables
        score = [0, 0]
        round_over = False
        ROUND_COOLDOWN = 5000 # ms, 5s

        ### Load background music
        pygame.mixer.music.load("assets/audio/Filip Lackovic - Drums of the Horde.mp3")  
        pygame.mixer.music.play(-1, 0.0, 5000)

        ### Load background image
        bg_image = pygame.image.load("assets/images/background/bg-dark-forest.jpg").convert_alpha()

        ### Load countdown image
        countdown = pygame.image.load("assets/images/text/countdown.png")
        countdown_list = []
        for steps in range(3):
            temp_img = countdown.subsurface(steps * 152, 0, 152, 188)
            countdown_list.append(temp_img)

        ### Fonts
        victory_font = pygame.font.Font("assets/fonts/turok.ttf", 100)
        score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)

        ### Frames per animations
        DREAMER_ANIMATION_FRAMES = [8, 9, 1, 7, 5, 3, 9]
        WARRIOR_ANIMATION_FRAMES = []

        print("Drawing assets on the screen...")

        # print("Loading images for sprites")
        animationList1 = loadImages("assets/images/dreamer/Sprites/dreamer.png", DREAMER_ANIMATION_FRAMES)
        animationList2 = loadImages("assets/images/dreamer/Sprites/dreamer.png", DREAMER_ANIMATION_FRAMES)

        ### Create thread for quitting
        quit_thread = threading.Thread(target=quit_game, args=(client,))
        quit_thread.start()

        ### Get fighter objects from network
        fighter_1 = get_player(name, client)
        # print(fighter_1)
        if fighter_1 == "error":
            print("MAJOR ERROR")
            return
        fighter_2 = get_player(opponentName, client)
        # print(fighter_2)
        if fighter_2 == "error":
            print("MAJOR ERROR")
            return

        ### Create thread for networking
        network_thread = threading.Thread(target=networking, args=(fighter_1,client,))
        network_thread.start()
        
        new_game = True
        while new_game:
            intro_count = 3
            last_count_update = pygame.time.get_ticks()
            print("Starting new game..")
            run = True
            while run:
                if lost_conn == True:
                    print("Lost connection")
                    new_game = False
                    break
                clock.tick(FPS)

                ### Drawing background & health bars
                # print("Drawing background and health bars")
                scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                screen.blit(scaled_bg, (0,0))

                if fighter_1.opp == False:
                    draw_health_bar(fighter_1.health, 20, 20, screen)
                    draw_health_bar(fighter_2.health, 580, 20, screen)
                    writeText(fighter_1.playerID + ": " + str(score[0]), score_font, RED, 20, 60, screen)
                    writeText(fighter_2.playerID + ": " + str(score[1]), score_font, RED, 580, 60, screen)
                else:
                    draw_health_bar(fighter_2.health, 20, 20, screen)
                    draw_health_bar(fighter_1.health, 580, 20, screen)
                    writeText(fighter_2.playerID + ": " + str(score[0]), score_font, RED, 20, 60, screen)
                    writeText(fighter_1.playerID + ": " + str(score[1]), score_font, RED, 580, 60, screen)

                # print(f"Drawn the assets: {scaled_bg}")

                if intro_count <= 0:
                    fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_2)
                else:
                    screen.blit(countdown_list[intro_count-1], (SCREEN_WIDTH / 2.5, SCREEN_HEIGHT / 6))
                    if (pygame.time.get_ticks() - last_count_update) >= 1000:
                        intro_count -= 1
                        last_count_update = pygame.time.get_ticks()

                ### Animate sprites and handle input
                # print("Animating sprites and handling inputs")
                fighter_1.animate(animationList1)
                img1 = pygame.transform.flip(fighter_1.image, fighter_1.flip, False)
                screen.blit(img1, (fighter_1.pos.x - (fighter_1.imageOffset[0] * fighter_1.imageScale), fighter_1.pos.y - (fighter_1.imageOffset[1] * fighter_1.imageScale)))
                
                fighter_2.animate(animationList2)
                img2 = pygame.transform.flip(fighter_2.image, fighter_2.flip, False)
                screen.blit(img2, (fighter_2.pos.x - (fighter_2.imageOffset[0] * fighter_2.imageScale), fighter_2.pos.y - (fighter_2.imageOffset[1] * fighter_2.imageScale)))

                ### Check whether the round is over
                # print("Checking whether round is over")
                if round_over == False:
                    if fighter_1.alive == False:
                        score[1] += 1
                        round_over = True
                        round_over_time = pygame.time.get_ticks()
                    elif fighter_2.alive == False:
                        score[0] += 1
                        round_over = True
                        round_over_time = pygame.time.get_ticks()
                    else:
                        pass 
                if round_over == True:
                    writeText("Victory", victory_font, RED, SCREEN_WIDTH / 3, SCREEN_HEIGHT / 5, screen)
                    if pygame.time.get_ticks() - round_over_time > ROUND_COOLDOWN:
                        # print("Resetting")
                        succesful = reset(fighter_1)
                        if succesful == 0:
                            print("Loading new game...")
                            round_over = False
                            run = False
                # Update display
                # print("Updating screen")
                pygame.display.flip()
        print("End game: Closing connection with server.")
        network_flag = False
        client.close()
        pygame.quit()
        new_game = False
        server_flag = False
    except Exception as e:
        print(f"Except: Closing connection with server, {e}")
        server_flag = True
        network_flag = False
        client.close()
        pygame.quit()
        exit(1)
##################################################################################################################
def main():
    client = None
    start(client)

main()
