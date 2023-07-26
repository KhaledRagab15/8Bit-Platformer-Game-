import pygame
from pygame.locals import *
import pickle
from os import path
from pygame import mixer

pygame.mixer.pre_init(44100, -16, 2, 10)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60
level = 1
max_levels = 4
score = 0


screen_width = 700
screen_height = 690

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("8 BIT PLATFORMER GAME")

#font
font_Score = pygame.font.SysFont("Arial", 24, "bold")
font = pygame.font.SysFont("Arial", 40, "bold")
font_menu = pygame.font.SysFont("Arial", 50)


#color
red = (255, 0, 0, 255)
purple = (160, 32, 240, 255)
yellow = (255, 255, 0, 255)
black = (0, 0, 0, 255)
orange = (255, 165, 0, 255)

#images
bg_img = pygame.image.load("images/586811-8-Bit-Empire.jpg")
img1 = pygame.transform.scale(bg_img, (670,670))
restart_img = pygame.image.load("images/restart.png")
img2 = pygame.transform.scale(restart_img, (100,100))
start_img = pygame.image.load("images/start.png")
img3 = pygame.transform.scale(start_img, (120,70))
exit_img = pygame.image.load("images/exit.png")
img4 = pygame.transform.scale(exit_img, (120,70))

#load sounds
coin_sfx = pygame.mixer.Sound("music-se/coin-collect-retro-8-bit-sound-effect-145251.mp3")
coin_sfx.set_volume(0.5)
jump_sfx = pygame.mixer.Sound("music-se/sfx_jump_07-80241.mp3")
jump_sfx.set_volume(0.5)
dead_sfx = pygame.mixer.Sound("music-se/videogame-death-sound-43894.mp3")
dead_sfx.set_volume(1)
pygame.mixer.music.load("music-se/8bit-music-for-game-68698.mp3")
pygame.mixer.music.play(-1, 0.0, 10000)
win_sfx = pygame.mixer.Sound("music-se/winsquare-6993.mp3")
win_sfx.set_volume(1)
#variables
tile_size = 35
game_over = 0
main_menu = True

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))
#reset level function
def reset_level(level):
    player.reset(90, screen_height - 100)
    enemy_group.empty()
    spike_group.empty()
    exit_group.empty()

    #load level
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
    def draw(self):
        action = False
        #get_mouse-position
        pos = pygame.mouse.get_pos()

        #get_mouseover_and_clicked_conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        #draw_button
        screen.blit(self.image, self.rect)

        return action


enemy_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()


class World():
    def __init__(self, data):
        self.tile_list = []
        #image
        brick_img = pygame.image.load("images/brick.png")
        platform_img = pygame.image.load("images/platform.png")

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(brick_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(platform_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    enemy = Enemy(col_count * tile_size, row_count * tile_size + 3)
                    enemy_group.add(enemy)
                if tile == 4:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 6:
                    spike = Spike(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    spike_group.add(spike)
                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])



class Enemy(pygame.sprite.Sprite):
    def __init__(self, x , y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/enemy.png")
        self.image = pygame.transform.scale(self.image, (30, 33))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 45:
            self.move_direction *= -1
            self.move_counter *= -1

class Platform(pygame.sprite.Sprite):
    def __init__(self, x , y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("images/platform.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 45:
            self.move_direction *= -1
            self.move_counter *= -1
class Spike(pygame.sprite.Sprite):
    def __init__(self, x , y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("images/spike.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

class Coin(pygame.sprite.Sprite):
    def __init__(self, x , y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("images/coin.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
    def __init__(self, x , y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("images/door.png")
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Player():
    def __init__(self, x, y):
        self.reset(x, y)
    def update(self, game_over):

        dx = 0
        dy = 0
        walk_cooldown = 6
        col_threshold = 20

        if game_over == 0:

            #keypresses

            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                self.rect.x -= 3
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                self.rect.x += 3
                self.counter += 1
                self.direction = 1
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_sfx.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            #animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            #adding gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            #collision
            self.in_air = True
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if below the ground
                    if self.vel_y < 0:
                       dy = tile[1].bottom - self.rect.top
                       self.vel_y = 0
                    # check if above the ground
                    elif self.vel_y >= 0:
                       dy = tile[1].top - self.rect.bottom
                       self.vel_y = 0
                       self.in_air = False

            if self.rect.bottom > screen_height:
                self.rect.bottom = screen_height
                dy = 0

            #collision with enemies
            if pygame.sprite.spritecollide(self, enemy_group, False):
                game_over = -1
                dead_sfx.play()

            # collision with spike
            if pygame.sprite.spritecollide(self, spike_group, False):
                game_over = -1
                dead_sfx.play()

            # collision with door
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = +1

            #collision with platforms
            for platform in platform_group:
                #collision in x direction
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    dx = 0
                # collision in y direction
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if below platform
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_threshold:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    # check if above platform
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_threshold:
                        self.rect.bottom = platform.rect.top - 1
                        dy = 0
                        self.in_air = False
                    #move sideways with the platform
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

        #player coordinates
        self.rect.x += dx
        self.rect.y += dy

        if game_over == -1:
            self.image = self.dead_image
            draw_text("GAME OVER", font, black, (screen_width // 2) - 100, screen_height // 2 - 150)
            if self.rect.y > 150:
                self.rect.y -= 50
        #draw player onto screen
        screen.blit(self.image, self.rect)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 3):
            img_right = pygame.image.load(f"images/person{num}.png")
            img_right = pygame.transform.scale(img_right, (25, 50))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load("images/dead.png")
        self.dead_image = pygame.transform.scale(self.dead_image, (26, 50))
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


# create dummy coin for showing score
score_coin = Coin(tile_size // 1, tile_size // 1.5)
coin_group.add(score_coin)

# load in level data and create world
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)
player = Player(90, screen_height - 100)

#create-buttons
restart_button = Button(screen_width // 2 - 50, screen_height // 2 , img2)
start_button = Button(screen_width // 2 - 140, screen_height // 2, img3)
exit_button = Button(screen_width // 2 + 60, screen_height // 2, img4)



run = True
while run:

    clock.tick(fps)
    screen.blit(img1, (0,0))

    if main_menu == True:
        draw_text("8 BIT PLATFORMER GAME", font_menu, black, (screen_width // 2) - 240, screen_height // 2 - 150)
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        world.draw()

        if game_over == 0:
            enemy_group.update()
            platform_group.update()
            #update_score
            #check if coin has been collected in the game
            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
                coin_sfx.play()
            draw_text('  X '+ str(score), font_Score, orange, tile_size + 10, 10)

        game_over = player.update(game_over)
       

        #if character died
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0

        #if player completed the level
        if game_over == 1:
            level += 1
            if level <= max_levels:
                #reset level
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text("YOU WIN!", font, black, (screen_width // 2) - 85, screen_height // 2 - 150)
                if win_sfx.play():
                    pygame.mixer.music.pause()

                if restart_button.draw():
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0


        platform_group.draw(screen)
        enemy_group.draw(screen)
        spike_group.draw(screen)
        exit_group.draw(screen)
        coin_group.draw(screen)



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()