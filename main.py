import os
import time
import random

import pygame

pygame.font.init()
GAME_FONT = pygame.font.SysFont('arial', 40)
MENU_FONT = pygame.font.SysFont('arial', 80)
GITHUB_FONT = pygame.font.SysFont('arial', 10)

WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Spaceship game')

# Enemy ships
ENEMY_SHIP1 = pygame.transform.flip(pygame.image.load(os.path.join('assets', 'img', 'enemy_ship1.png')), True, False)
ENEMY_SHIP2 = pygame.transform.flip(pygame.image.load(os.path.join('assets', 'img', 'enemy_ship2.png')), True, False)
ENEMY_SHIP3 = pygame.transform.flip(pygame.image.load(os.path.join('assets', 'img', 'enemy_ship3.png')), True, False)

# Player ship
PLAYER_SHIP = pygame.image.load(os.path.join('assets', 'img', 'player_ship.png'))

# Lasers
PLAYER_LASER = pygame.image.load(os.path.join('assets', 'img', 'player_laser.png'))
ENEMY_LASER = pygame.image.load(os.path.join('assets', 'img', 'enemy_laser.png'))

# Props
METEOR1 = pygame.image.load(os.path.join('assets', 'img', 'meteor1.png'))
METEOR2 = pygame.image.load(os.path.join('assets', 'img', 'meteor2.png'))
DESTROY_ENEMY_BONUS = pygame.image.load(os.path.join('assets', 'img', 'destroy_enemy_bonus.png'))
ENEMY_SPEED_DEBUFF = pygame.image.load(os.path.join('assets', 'img', 'enemy_speed_debuff.png'))
FIRE_RATE_BONUS = pygame.image.load(os.path.join('assets', 'img', 'fire_rate_bonus.png'))
HP_BONUS = pygame.image.load(os.path.join('assets', 'img', 'hp_bonus.png'))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'img', 'background.png')), (WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.x += vel

    def off_screen(self, width):
        return not (self.x >= 0 and self.x <= width)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cooldown_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(WIDTH):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SHIP
        self.laser_img = PLAYER_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(WIDTH):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x + 80, self.y + 55, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x + 25, self.y + 20, 80, 7))
        pygame.draw.rect(window, (0,255,0), (self.x + 25, self.y + 20, 80 * (self.health/self.max_health), 7))

    def draw(self, window):
        super().draw(window)  
        self.healthbar(window)              

class Enemy(Ship):
    ENEMY_SHIPS = {
        1 : ENEMY_SHIP1,
        2 : ENEMY_SHIP2,
        3 : ENEMY_SHIP3
    }

    def __init__(self, x, y, type, health=100):
        super().__init__(x, y, health)
        self.ship_img = self.ENEMY_SHIPS[type]
        self.laser_img = ENEMY_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.x -= vel

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x, self.y + self.get_height()/5, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    player_vel = 5
    lost = False
    lost_count = 0
    enemies = []
    wave_length = 5
    enemy_vel = 1
    laser_vel = 5

    clock = pygame.time.Clock()

    player = Player(100, 300)

    def draw_window():
        WIN.blit(BG, (0, 0))

        lives_label = GAME_FONT.render(f'Lives: {lives}', 1, (255,255,255))
        level_label = GAME_FONT.render(f'Level: {level}', 1, (255,255,255))
        
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = MENU_FONT.render('You lost!', 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 300))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        draw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 4: # Showing 'You lost!' message for 4 seconds
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 2
            for i in range(wave_length):
                enemy = Enemy(random.randrange(WIDTH+100, WIDTH+1000+level*50), random.randrange(100, HEIGHT-100), random.randrange(1,4))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # Left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # Right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel + 50 > 0: # Up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() - 50 < HEIGHT: # Down
            player.y += player_vel
        if keys[pygame.K_SPACE]: # Shoot
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(-laser_vel, player)

            if random.randrange(0, 4*FPS) == 1: # Every second enemy has a 25% chance of shooting
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.x + enemy.get_width() < 0:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(laser_vel, enemies) # add meteors

def main_menu():
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = MENU_FONT.render('Press ANY KEY to begin', 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 300))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()

main_menu()

