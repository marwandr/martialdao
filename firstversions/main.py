import pygame
from network import Network
from pygame import mixer

server = Network()
print("test")
fighter_1 = server.get_player()

mixer.init()
pygame.init()

# Create the game window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Martial Dao")

# Set framerate
clock = pygame.time.Clock()
FPS = 60

# Colors
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game variables
intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0, 0]
round_over = False
ROUND_COOLDOWN = 10000 # ms, 10s
LOST_CONNECTION_LIMIT = 30000 # ms, 30s

# Sprite variables
SPRITE_SIZE = 162
SPRITE_SCALE = 4
SPRITE_OFFSET = [72, 56]

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

def writeText(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

# Frames per animations
DREAMER_ANIMATION_FRAMES = [8, 9, 1, 7, 5, 3, 9]
WARRIOR_ANIMATION_FRAMES = [10, 8, 1, 7, 7, 3, 7]
CHRONOMAGE_ANIMATION_FRAMES = [10, 8, 1, 7, 7, 3, 7]

# Drawing background
def draw_bg():
    scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0,0))

# Drawing health bars
def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, BLACK, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))

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

# create two instances of fighters
print("getting data")
fighter_1 = server.get_player()

run = True
while run:
    if fighter_1 is None:
        fighter_1 = server.get_player()
        continue
    fighter_2 = server.send(fighter_1)
    clock.tick(FPS)

    if fighter_2 is None:
        print("Waiting for opponent...")
        continue

    draw_bg()
    draw_health_bar(fighter_1.health, 20, 20)
    draw_health_bar(fighter_2.health, 580, 20)

    writeText("P1: " + str(score[0]), score_font, RED, 20, 60)
    writeText("P2: " + str(score[1]), score_font, RED, 580, 60)

    if intro_count <= 0:
        fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, fighter_2)
    else:
        screen.blit(countdown_list[intro_count-1], (SCREEN_WIDTH / 2.5, SCREEN_HEIGHT / 6))
        if (pygame.time.get_ticks() - last_count_update) >= 1000:
            intro_count -= 1
            last_count_update = pygame.time.get_ticks()

    animationList1 = loadImages("assets/images/dreamer/Sprites/dreamer.png", DREAMER_ANIMATION_FRAMES)
    animationList2 = loadImages("assets/images/dreamer/Sprites/dreamer.png", DREAMER_ANIMATION_FRAMES)

    fighter_1.animate(animationList1)
    img1 = pygame.transform.flip(fighter_1.image, fighter_1.flip, False)
    screen.blit(img1, (fighter_1.pos.x - (fighter_1.imageOffset[0] * fighter_1.imageScale), fighter_1.pos.y - (fighter_1.imageOffset[1] * fighter_1.imageScale)))
    fighter_2 = server.send(fighter_1)
    if fighter_2 == "Time-out":
        fighter_2 = server.send(fighter_1)
        lost_connection_time = pygame.time.get_ticks()
    while fighter_2 == "Time-out":
        fighter_2 = server.send(fighter_1)
        if (pygame.time.get_ticks() - lost_connection_time) > LOST_CONNECTION_LIMIT:
            writeText("User disconnected", victory_font, BLACK, SCREEN_WIDTH / 3, SCREEN_HEIGHT / 5)
            fighter_1 = server.end_connection()
            server = Network()
            fighter_1 = server.get_player()
            pygame.display.update()
            continue

    fighter_2.animate(animationList2)
    img2 = pygame.transform.flip(fighter_2.image, fighter_2.flip, False)
    screen.blit(img2, (fighter_2.pos.x - (fighter_2.imageOffset[0] * fighter_2.imageScale), fighter_2.pos.y - (fighter_2.imageOffset[1] * fighter_2.imageScale)))

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
        writeText("Victory", victory_font, RED, SCREEN_WIDTH / 3, SCREEN_HEIGHT / 5)
        fighter_1 = server.end_connection()
        server = Network()
        fighter_1 = server.get_player()
        if pygame.time.get_ticks() - round_over_time > ROUND_COOLDOWN:
            round_over = False
            intro_count = 3
            
    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # QUIT IF WINDOW IS CLOSED
            run = False

    # Update display
    pygame.display.update()
pygame.quit()
