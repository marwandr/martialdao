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
import gc

gc.enable()

opponent_name = None
start_game = False

def reset():
    client.sendto("RESET".encode(), (host_address, host_port))
    data, _ = client.recvfrom(2048)
    try:
        if data.decode() == "RESET-SUCCESS":
            return 0
        else:
            return 1
    except:
        return 1

def get_player(ID):
    client.sendto(f"FIGHTER-{ID}".encode(), (host_address, host_port))
    data, _ = client.recvfrom(2048)
    try:
        print(pickle.loads(data))
        return pickle.loads(data)
    except:
        if data.decode() == "WRONG-ID":
            print("Something went wrong while requesting player information, please try again.")
            print(data.decode())
            client.close()
            return "error"
        elif "ACCEPTED" in data.decode():
            return get_player(ID)
        else:
            print("Something went wrong while requesting player information, please try again.")
            print(data.decode())
            client.close()
            return "error"
    
def send_player(player):
    client.sendto(pickle.dumps(player), (host_address, host_port))
    # print("Receiving")
    data, _ = client.recvfrom(2048)
    # print("Received")
    try:
        # print(pickle.loads(data))
        return pickle.loads(data)
    except:
        if data.decode() == "WRONG-ID":
            print("Something went wrong while requesting player information, please try again.")
            client.close()
            return "error"

def receive():
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


server_address = '127.0.0.1'
server_port = random.randint(8000, 9000)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind((server_address, server_port))

name = input("Nickname: ")
opponent_name = None
serverqueue = queue.Queue()

while True:
    host = input("Do you want to host? (y/n)\n") == "y"
    if host:
        s = threading.Thread(target=start_server,args=(serverqueue,))
        s.start()
        host_address = serverqueue.get(True)
        host_port = serverqueue.get(True)
        print(f"Server address: {host_address}\nServer port: {host_port}")
        print("Connecting...")
        break
    else:
        host_address = input("What is the address of the host you want to join?\n")
        if host_address == "local":
            host_address = '127.0.0.1'
        try:
            host_port = int(input("What is the port?\n"))
        except:
            continue
        print("Connecting...")
        break

receive_thread = True
t = threading.Thread(target=receive)
t.start()
while not start_game:
    client.sendto(f"CONNECT_REQ:{name}".encode(), (host_address, host_port))
print("Opponent connected. Commencing battlefield...")
t.join()

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

# Function for sending & receiving data thread
def networking(fighter_1):
    global fighter_2
    while True:
        fighter_2 = send_player(fighter_1)

# Function for quitting game thread
def quit_game():
    global run
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                client.close()
                pygame.quit()
                exit()

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
def game(opponentName):
    global name
    global receive_thread
    global fighter_2
    # Stop thread for receiving & start thread to check for quitting game
    receive_thread = False
    quit_thread = threading.Thread(target=quit_game)
    quit_thread.start()
    pygame.init()
    mixer.init()

    try:
        new_game = True
        while new_game:
            print("Starting new game...")
            # Get fighter object from network
            fighter_1 = get_player(name)
            # print(fighter_1)
            if fighter_1 == "error":
                print("MAJOR ERROR")
                return
            
            # Get object of player 2 through network
            fighter_2 = get_player(opponentName)
            # print(fighter_2)
            if fighter_2 == "error":
                print("MAJOR ERROR")
                return
            
            print("Creating game window...")

            # Create the game window
            SCREEN_WIDTH = 1000
            SCREEN_HEIGHT = 600

            screen = pygame.display.set_mode((500, 500))
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Martial Dao")

            # Set framerate
            clock = pygame.time.Clock()
            FPS = 20

            # Game variables
            intro_count = 3
            last_count_update = pygame.time.get_ticks()
            score = [0, 0]
            round_over = False
            ROUND_COOLDOWN = 10000 # ms, 10s

            # Load background music
            pygame.mixer.music.load("assets/audio/Filip Lackovic - Drums of the Horde.mp3")  
            pygame.mixer.music.play(-1, 0.0, 5000)

            # Load background image
            bg_image = pygame.image.load("assets/images/background/bg-dark-forest.jpg").convert_alpha()

            # Load countdown image
            countdown = pygame.image.load("assets/images/text/countdown.png")
            countdown_list = []
            for steps in range(3):
                temp_img = countdown.subsurface(steps * 152, 0, 152, 188)
                countdown_list.append(temp_img)

            # Fonts
            victory_font = pygame.font.Font("assets/fonts/turok.ttf", 100)
            score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)

            # Frames per animations
            DREAMER_ANIMATION_FRAMES = [8, 9, 1, 7, 5, 3, 9]

            network_thread = threading.Thread(target=networking, args=(fighter_1,))
            network_thread.start()

            print("Drawing assets on the screen...")

            # print("Loading images for sprites")
            animationList1 = loadImages("assets/images/dreamer/Sprites/dreamer.png", DREAMER_ANIMATION_FRAMES)
            animationList2 = loadImages("assets/images/dreamer/Sprites/dreamer.png", DREAMER_ANIMATION_FRAMES)

            run = True
            while run:
                clock.tick(FPS)

                # Drawing background
                # print("Drawing background and health bars")
                scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                screen.blit(scaled_bg, (0,0))

                draw_health_bar(fighter_1.health, 20, 20, screen)
                draw_health_bar(fighter_2.health, 580, 20, screen)

                writeText(fighter_1.playerID + ": " + str(score[0]), score_font, RED, 20, 60, screen)
                writeText(fighter_2.playerID + ": " + str(score[1]), score_font, RED, 580, 60, screen)
                # print(f"Drawn the assets: {scaled_bg}")

                if intro_count <= 0:
                    fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_2)
                else:
                    screen.blit(countdown_list[intro_count-1], (SCREEN_WIDTH / 2.5, SCREEN_HEIGHT / 6))
                    if (pygame.time.get_ticks() - last_count_update) >= 1000:
                        intro_count -= 1
                        last_count_update = pygame.time.get_ticks()

                # Animate sprites and handle input
                # print("Animating sprites and handling inputs")
                fighter_1.animate(animationList1)
                img1 = pygame.transform.flip(fighter_1.image, fighter_1.flip, False)
                screen.blit(img1, (fighter_1.pos.x - (fighter_1.imageOffset[0] * fighter_1.imageScale), fighter_1.pos.y - (fighter_1.imageOffset[1] * fighter_1.imageScale)))
                
                # Send object of fighter 1 and update fighter 2
                # print("Checking to send player")
                # fighter_2 = send_player(fighter_1) 
                # print(fighter_2)
                # if fighter_2 == "error":
                #     print("MAJOR ERROR")
                #     return
                # print("Checking to animate fighter 2")
                fighter_2.animate(animationList2)

                # print("Checking to flip image 2")
                img2 = pygame.transform.flip(fighter_2.image, fighter_2.flip, False)

                # print(f"Blitting fighter 2")
                screen.blit(img2, (fighter_2.pos.x - (fighter_2.imageOffset[0] * fighter_2.imageScale), fighter_2.pos.y - (fighter_2.imageOffset[1] * fighter_2.imageScale)))

                # print("Checking whether round is over")
                # Check whether the round is over
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
                    if fighter_2.alive == False:
                        writeText("Victory", victory_font, RED, SCREEN_WIDTH / 3, SCREEN_HEIGHT / 5, screen)
                    else:
                        writeText("Loss", victory_font, RED, SCREEN_WIDTH / 3, SCREEN_HEIGHT / 5, screen)
                    if pygame.time.get_ticks() - round_over_time > ROUND_COOLDOWN:
                        succesful = reset()
                        if succesful == 0:
                            round_over = False
                            run = False
                            network_thread.join()
                            pass
                # Update display
                # print("Updating screen")
                pygame.display.flip()

            client.close()
            pygame.quit()
            new_game = False
    except:
        client.close()
        pygame.quit()
        exit(1)
##################################################################################################################

if opponent_name == "error":
    print("Exiting...")
    client.close()
else:
    game(opponent_name)
    exit(0)
