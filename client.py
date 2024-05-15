# With help from: https://www.youtube.com/watch?v=s5bd9KMSSW4

import socket
import threading
import random
import linecache
import pickle
import pygame
from cultivator import Cultivator
from pygame import mixer

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(('127.0.0.1', random.randint(8000, 9000)))

name = input("Nickname: ")
opponent_name = None

def reset():
    client.sendto(f"RESET".encode(), ('127.0.0.1', 8000))
    data, _ = client.recvfrom(2048)
    return data.decode()

def get_player(ID):
    client.sendto(f"FIGHTER-{ID}".encode(), ('127.0.0.1', 8000))
    data, _ = client.recvfrom(2048)
    try:
        print(pickle.loads(data))
        return pickle.loads(data)
    except:
        if data.decode() == "WRONG-ID":
            print("Something went wrong while requesting player information, please try again.")
            client.close()
            return "error"
        else:
            print("Something went wrong while requesting player information, please try again.")
            print(data.decode())
            client.close()
            return "error"
    
def send_player(player):
    client.sendto(pickle.dumps(player), ('127.0.0.1', 8000))
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
    while receive_thread:
        try:
            data, _ = client.recvfrom(2048)
            if "ACCEPTED" in data.decode():
                opponent_name = data.decode()[data.decode().index(":")+1:]
                receive_thread = False
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
            elif data.decode().startswith("CONNECT_REQ:"):
                playerName = data.decode()[data.decode().index(":")+1:]
                print(f"{playerName} has joined your match!")
                accept = input("Accept? (y/n)")
                if accept == "y":
                    client.sendto(f"ACCEPTED:{name}".encode(), ('127.0.0.1', 8000))
                    opponent_name = playerName
                    receive_thread = False
                elif accept == "n":
                    client.sendto("REJECTED".encode(), ('127.0.0.1', 8000))
                    continue
                else:
                    print("Please enter either 'y' to accept or 'n' to reject.")
                    again = linecache.getline(__file__, 54)
                    exec(again)                    
            else:
                print("Something has gone wrong. Please try again.")
                client.close()
                opponent_name = "Error"
                receive_thread = False
        except:
            pass

receive_thread = True
t = threading.Thread(target=receive)
t.start()

client.sendto(f"CONNECT_REQ:{name}".encode(), ('127.0.0.1', 8000))
print("Please wait while someone joins your match.")
t.join()

#################--MAIN GAME--##########################################
# Colors
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Sprite variables
SPRITE_SIZE = 162
SPRITE_SCALE = 4
SPRITE_OFFSET = [72, 56]

# Function for quitting game thread
def quit_game():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                client.close()
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
    # Stop thread for receiving & start thread to check for quitting game
    receive_thread = False
    quit_thread = threading.Thread(target=quit_game)
    quit_thread.start()
    pygame.init()
    mixer.init()

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

    print("test")

    # Set framerate
    clock = pygame.time.Clock()
    FPS = 100

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
    bg_image = pygame.image.load("assets/images/background/background.jpg").convert_alpha()

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

    print("Drawing assets on the screen...")

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

        # print("Loading images for sprites")
        animationList1 = loadImages("assets/images/dreamer/Sprites/dreamer.png", DREAMER_ANIMATION_FRAMES)
        animationList2 = loadImages("assets/images/dreamer/Sprites/dreamer.png", DREAMER_ANIMATION_FRAMES)

        # Animate sprites and handle input
        # print("Animating sprites and handling inputs")
        fighter_1.animate(animationList1)
        img1 = pygame.transform.flip(fighter_1.image, fighter_1.flip, False)
        screen.blit(img1, (fighter_1.pos.x - (fighter_1.imageOffset[0] * fighter_1.imageScale), fighter_1.pos.y - (fighter_1.imageOffset[1] * fighter_1.imageScale)))
        
        # Send object of fighter 1 and update fighter 2
        # print("Checking to send player")
        fighter_2 = send_player(fighter_1) 
        # print(fighter_2)
        if fighter_2 == "error":
            print("MAJOR ERROR")
            return
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
        else:
            writeText("Victory", victory_font, RED, SCREEN_WIDTH / 3, SCREEN_HEIGHT / 5)
            if pygame.time.get_ticks() - round_over_time > ROUND_COOLDOWN:
                succesful = reset()
                if succesful == True:
                    round_over = False
                    intro_count = 3
                    pass

        # Update display
        # print("Updating screen")
        pygame.display.flip()
    client.close()
    pygame.quit()
##################################################################################################################

if opponent_name == "error":
    print("Exiting...")
    client.close()
else:
    game(opponent_name)
