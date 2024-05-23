import pygame

class Cultivator():
    def __init__(self, x, y, flip, data, spritesheet, animationSteps, opponent, server):
        self.connecting = True
        self.server = server
        self.opp = opponent
        self.size = data[0]
        self.imageScale = data[1]
        self.imageOffset = data[2]
        self.flip = flip
        self.animationList = self.loadImages(spritesheet, animationSteps)
        self.action = 0 # 0: Idle, 1: Run, 2: Jump, 3: Attack, 4: Defend, 5: Hit, 6: Death
        self.frame_index = 0
        self.image = self.animationList[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.defending = False
        self.hit = False
        self.alive = True
        self.attack_type = 0
        self.attack_cooldown = 0
        # Dreamer swoosh sound Effect by floraphonic from Pixabay
        self.attack_sound = pygame.mixer.Sound("assets/audio/dreamer_swoosh.mp3")
        self.death_sound = pygame.mixer.Sound("assets/audio/dreamer_death.mp3")
        self.defend_cooldown = 0
        self.health = 100
        self.dexterity = 30

    def loadImages(self, spritesheet, animationSteps):
        animationList = []
        for y, animation in enumerate(animationSteps):
            temp_img_list = []
            for steps in range(animation):
                temp_img = spritesheet.subsurface(steps * self.size, y * self.size, self.size, self.size)
                temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.imageScale, self.size * self.imageScale)))
            animationList.append(temp_img_list)
        return animationList

    def move(self, screen_width, screen_height, target):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        # Handle keyboard input
        if self.attacking == False and self.defending == False and self.alive == True:
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                dx = -SPEED
                self.running = True
            if key[pygame.K_RIGHT]:
                dx = SPEED
                self.running = True
            if key[pygame.K_UP] and self.jump is False:
                self.vel_y = -30
                self.jump = True
            if key[pygame.K_z]:
                self.attack(target)
                self.attack_type = 1
            if key[pygame.K_x]:
                self.defend(target)

        # Apply gravity to jump
        self.vel_y += GRAVITY
        dy += self.vel_y

        # Ensuring player won't go off-screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom
        
        # Ensure players face each other
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.defend_cooldown > 0:
            self.defend_cooldown -= 1

        self.rect.x += dx
        self.rect.y += dy

    # Handle animation
    def animate(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.death_sound.play()
            self.update_action(6)
        elif self.hit == True:
            self.update_action(5)
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(3)
        elif self.defending == True:
            self.update_action(4)
        elif self.jump == True:
            self.update_action(2)
        elif self.running == True:
            self.update_action(1)
        else:
            self.update_action(0)

        animation_cooldown = 50
        self.image = self.animationList[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.animationList[self.action]):
            if self.alive == False:
                self.frame_index = len(self.animationList[self.action]) - 1
            else:
                self.frame_index = 0
                if self.action == 3:
                    self.attacking = False
                    self.attack_cooldown = 50 - self.dexterity
                if self.action == 4:
                    self.defending = False
                    self.defend_cooldown = 50 - self.dexterity
                if self.action == 5:
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 50 - self.dexterity

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            self.attack_sound.play()
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.health -= 10 # Damage done by the attack
                target.hit = True

    def defend(self, target):
        if self.defend_cooldown == 0:
            self.defending = True
            defending_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
            if defending_rect.colliderect(target.rect):
                if target.attacking is True:
                    self.health += 10
                    self.hit = False

    def read_start_position(self):
        pos_str = self.server.get_pos()
        pos = pos_str.split(',')
        return int(pos[0]), int(pos[1])
    
    def read_position(self, target):
        pos_str = self.server.send(self.make_position((target.rect.x, target.rect.y)))
        pos = pos_str.split(',')
        return int(pos[0]), int(pos[1])
    
    def make_position(self, tup):
        position = str(tup[0]) + "," + str(tup[1])
        return position

    def update(self, surface, target):
        if self.opp == True:
            if self.connecting == True:
                oppPosition = self.read_start_position()
                self.rect.x = oppPosition[0]
                self.rect.y = oppPosition[1]
                img = pygame.transform.flip(self.image, self.flip, False)
                surface.blit(img, (self.rect.x - (self.imageOffset[0] * self.imageScale), self.rect.y - (self.imageOffset[1] * self.imageScale)))
                self.connecting = False
            else:
                oppPosition = self.read_position(target)
                self.rect.x = oppPosition[0]
                self.rect.y = oppPosition[1]
                img = pygame.transform.flip(self.image, self.flip, False)
                surface.blit(img, (self.rect.x - (self.imageOffset[0] * self.imageScale), self.rect.y - (self.imageOffset[1] * self.imageScale)))
        else:
            img = pygame.transform.flip(self.image, self.flip, False)
            surface.blit(img, (self.rect.x - (self.imageOffset[0] * self.imageScale), self.rect.y - (self.imageOffset[1] * self.imageScale)))
