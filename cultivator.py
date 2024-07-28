import pygame
pygame.init()

class Cultivator():
    def __init__(self, x, y, flip, data, playerID, opp):
        self.playerID = playerID
        self.connecting = True
        self.size = data[0]
        self.imageScale = data[1]
        self.imageOffset = data[2]
        self.flip = flip
        self.opp = opp
        self.action = 0 # 0: Idle, 1: Run, 2: Jump, 3: Attack, 4: Defend, 5: Hit, 6: Death
        self.frame_index = 0
        self.image = None
        self.update_time = pygame.time.get_ticks()
        self.pos = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.defending = False
        self.damage_done = 0
        self.hit = False
        self.alive = True
        self.attack_type = 0
        self.attack_cooldown = 0
        self.defend_cooldown = 0
        self.health = 100
        self.dexterity = 30

    def __getstate__(self):
        state = self.__dict__.copy()
        state['rect'] = (self.pos.x, self.pos.y, self.pos.width, self.pos.height)
        del state['image']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.pos = pygame.Rect(state['rect'])
        self.image = None

    def move(self, screen_width, screen_height, target):
        SPEED = 10
        GRAVITY = 3
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        if target.attacking == True:
            self.health -= target.damage_done
            self.hit = True

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
        if self.pos.left + dx < 0:
            dx = -self.pos.left
        if self.pos.right + dx > screen_width:
            dx = screen_width - self.pos.right
        if self.pos.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.pos.bottom
        
        # Ensure players face each other
        if target.pos.centerx > self.pos.centerx:
            self.flip = False
        else:
            self.flip = True

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.defend_cooldown > 0:
            self.defend_cooldown -= 1

        self.pos.x += dx
        self.pos.y += dy

    # Handle animation
    def animate(self, animationList):
        if self.health <= 0:
            self.health = 0
            self.alive = False
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

        animation_cooldown = 20
        self.image = animationList[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(animationList[self.action]):
            if self.alive == False:
                self.frame_index = len(animationList[self.action]) - 1
            else:
                self.frame_index = 0
                if self.action == 3:
                    self.attacking = False
                    self.damage_done = 0
                    self.attack_cooldown = 35 - self.dexterity
                if self.action == 4:
                    self.defending = False
                    self.defend_cooldown = 35 - self.dexterity
                if self.action == 5:
                    self.hit = False
                    self.attacking = False
                    self.damage_done = 0
                    self.attack_cooldown = 32 - self.dexterity

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            attacking_rect = pygame.Rect(self.pos.centerx - (2 * self.pos.width * self.flip), self.pos.y, 2 * self.pos.width, self.pos.height)
            if attacking_rect.colliderect(target.pos):
                self.damage_done = 1 # Damage done by the attack

    def defend(self, target):
        if self.defend_cooldown == 0:
            self.defending = True
            defending_rect = pygame.Rect(self.pos.centerx - (2 * self.pos.width * self.flip), self.pos.y, 2 * self.pos.width, self.pos.height)
            if defending_rect.colliderect(target.pos):
                if target.attacking is True:
                    self.health += 10
                    self.hit = False
    
    def get_player(self):
        player_data = self.server.send(Cultivator())
        for attr in vars(player_data):
            setattr(self, attr, getattr(player_data, attr))


class Warrior():
    def __init__(self, x, y, flip, data, playerID, opp):
        self.playerID = playerID
        self.connecting = True
        self.size = data[0]
        self.imageScale = data[1]
        self.imageOffset = data[2]
        self.flip = flip
        self.opp = opp
        self.action = 0 # 0: Idle, 1: Run, 2: Jump, 3: Attack, 4: Defend, 5: Hit, 6: Death
        self.frame_index = 0
        self.image = None
        self.update_time = pygame.time.get_ticks()
        self.pos = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.defending = False
        self.damage_done = 0
        self.hit = False
        self.alive = True
        self.attack_type = 0
        self.attack_cooldown = 0
        self.defend_cooldown = 0
        self.health = 100
        self.dexterity = 50

    def __getstate__(self):
        state = self.__dict__.copy()
        state['rect'] = (self.pos.x, self.pos.y, self.pos.width, self.pos.height)
        del state['image']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.pos = pygame.Rect(state['rect'])
        self.image = None

    def move(self, screen_width, screen_height, target):
        SPEED = 10
        GRAVITY = 3
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        if target.attacking == True:
            self.health -= target.damage_done
            self.hit = True

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
        if self.pos.left + dx < 0:
            dx = -self.pos.left
        if self.pos.right + dx > screen_width:
            dx = screen_width - self.pos.right
        if self.pos.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.pos.bottom
        
        # Ensure players face each other
        if target.pos.centerx > self.pos.centerx:
            self.flip = False
        else:
            self.flip = True

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.defend_cooldown > 0:
            self.defend_cooldown -= 1

        self.pos.x += dx
        self.pos.y += dy

    # Handle animation
    def animate(self, animationList):
        if self.health <= 0:
            self.health = 0
            self.alive = False
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

        animation_cooldown = 20
        self.image = animationList[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(animationList[self.action]):
            if self.alive == False:
                self.frame_index = len(animationList[self.action]) - 1
            else:
                self.frame_index = 0
                if self.action == 3:
                    self.attacking = False
                    self.damage_done = 0
                    self.attack_cooldown = 35 - self.dexterity
                if self.action == 4:
                    self.defending = False
                    self.defend_cooldown = 35 - self.dexterity
                if self.action == 5:
                    self.hit = False
                    self.attacking = False
                    self.damage_done = 0
                    self.attack_cooldown = 32 - self.dexterity

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            attacking_rect = pygame.Rect(self.pos.centerx - (2 * self.pos.width * self.flip), self.pos.y, 2 * self.pos.width, self.pos.height)
            if attacking_rect.colliderect(target.pos):
                self.damage_done = 1 # Damage done by the attack

    def defend(self, target):
        if self.defend_cooldown == 0:
            self.defending = True
            defending_rect = pygame.Rect(self.pos.centerx - (2 * self.pos.width * self.flip), self.pos.y, 2 * self.pos.width, self.pos.height)
            if defending_rect.colliderect(target.pos):
                if target.attacking is True:
                    self.health += 5
                    self.hit = False
    
    def get_player(self):
        player_data = self.server.send(Cultivator())
        for attr in vars(player_data):
            setattr(self, attr, getattr(player_data, attr))
