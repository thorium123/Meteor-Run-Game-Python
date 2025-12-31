import pygame
import random
from pygame import mixer
import os 
import math

# Initialize Pygame
pygame.init()
mixer.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Meteor Settings
object_width = 50
object_height = 50
fall_speed = 5

### Load music
mydir = os.path.dirname(os.path.realpath(__file__))

# Try/Except block in case music file is missing, prevents crash
try:
    mixer.music.load(fr'{mydir}/Music/tune_1.mp3')
    mixer.music.set_volume(0.03)
    mixer.music.play(loops=-1)
except pygame.error:
    print("Music file not found, running without music.")

# Screen dimensions and flags
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

flags = pygame.RESIZABLE | pygame.SCALED

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
pygame.display.set_caption("Meteor Run")

# Player settings
player_width = 100
player_height = 100
player_speed = 5
jump_height = 15
gravity = 1
ground_level = SCREEN_HEIGHT - player_height

# --- LOAD IMAGES ---
# Note: Background loading is moved to the Class below

player_image_left = pygame.image.load(fr'{mydir}/Images/Player.Left.png') 
player_image_left = pygame.transform.scale(player_image_left, (player_width, player_height))

player_image_right = pygame.image.load(fr'{mydir}/Images/Player.Right.png') 
player_image_right = pygame.transform.scale(player_image_right, (player_width, player_height))

player_image_default = pygame.image.load(fr'{mydir}/Images/Player.png') 
player_image_default = pygame.transform.scale(player_image_default, (player_width, player_height))

player_image = player_image_default  # Default image

meteor_image = pygame.image.load(fr'{mydir}/Images/Meteor.png')
meteor_image = pygame.transform.scale(meteor_image, (object_width, object_height))

cheese_image = pygame.image.load(fr'{mydir}/Images/Cheese.png') 
cheese_image = pygame.transform.scale(cheese_image, (object_width, object_height))

b_imgs = [pygame.image.load(fr'{mydir}/Images/Bullet-Red.png'), pygame.image.load(fr'{mydir}/Images/Bullet-Green.png')] 

bullet_image = random.choice(b_imgs)
bullet_image = pygame.transform.scale(bullet_image, (20, 30))

# --- NEW SCROLLING BACKGROUND CLASS ---
class ScrollingBackground:
    def __init__(self, screen_width, screen_height, image_path, speed):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = 2
        self.scroll = 0

        # Load and Scale Image
        self.bg_image = pygame.image.load(image_path).convert()
        self.bg_image = pygame.transform.scale(self.bg_image, (screen_width, screen_height))
        
        # Calculate how many tiles we need
        self.bg_height = self.bg_image.get_height()
        self.tiles = math.ceil(screen_height / self.bg_height) + 1

    def update(self):
        # Scroll moves DOWN (positive speed)
        self.scroll += self.speed

        # Reset scroll if it exceeds the image height
        if abs(self.scroll) > self.bg_height:
            self.scroll = 0

    def draw(self, screen):
        # Draw the background tiles
        # range(-1, tiles) ensures we draw the tile entering from the top
        for i in range(-1, self.tiles):
            y = i * self.bg_height + self.scroll
            screen.blit(self.bg_image, (0, y))

# --- CLASSES ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image_default
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, ground_level))
        self.speed = player_speed
        self.jump_speed = jump_height
        self.gravity = gravity
        self.vel_y = 0
        self.jumping = False
        self.lives = 10

    def move(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.rect.left > 0:
            self.rect.x -= self.speed
            self.image = player_image_left 
        elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
            self.image = player_image_right 
        else:
            self.image = player_image_default 

    def jump(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.jumping = True
            self.vel_y = -self.jump_speed

    def apply_gravity(self):
        if self.jumping:
            self.vel_y += self.gravity
            self.rect.y += self.vel_y
            if self.rect.bottom >= ground_level:
                self.rect.bottom = ground_level
                self.jumping = False

    def update(self):
        self.move()
        self.jump()
        self.apply_gravity()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = meteor_image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = fall_speed
        self.transformed = False

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()

    def transform_to_cheese(self):
        self.image = cheese_image
        self.transformed = True

    def reset(self):
        self.rect.bottom = 0
        self.rect.x = random.randint(0, SCREEN_WIDTH - object_width)
        self.image = meteor_image
        self.transformed = False

# --- SETUP OBJECTS ---
meteors = pygame.sprite.Group()
for _ in range(10):
    meteor = Meteor(random.randint(0, SCREEN_WIDTH - object_width), random.randint(-SCREEN_HEIGHT // 2, 0))
    meteors.add(meteor)

# Initialize Background Object
# Make sure "Images/Background.png" exists!
scrolling_bg = ScrollingBackground(SCREEN_WIDTH, SCREEN_HEIGHT, fr"{mydir}/Images/Background.png", speed=5)

def lives_to_words(lives):
    words = {
        10: "10 Lives", 9: "9 Lives", 8: "8 Lives", 7: "7 Lives", 6: "6 Lives",
        5: "5 Lives", 4: "4 Lives", 3: "3 Lives", 2: "2 Lives", 1: "1 Life", 0: "0 Lives"
    }
    return words.get(lives, str(lives))

def draw_lives_in_words(screen, lives):
    font = pygame.font.SysFont(None, 36)
    lives_text = font.render(f'Lives: {lives_to_words(lives)}', True, WHITE)
    screen.blit(lives_text, (10, 10))

# --- MAIN LOOP ---
clock = pygame.time.Clock()
player = Player()
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()

all_sprites.add(player)
all_sprites.add(meteors)

run = True

while run:
    # 1. Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                bullet = Bullet(player.rect.centerx, player.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)   

    # 2. Logic Updates
    scrolling_bg.update()  # Update background position
    all_sprites.update()   # Update player/meteors

    # Collisions
    collisions = pygame.sprite.groupcollide(bullets, meteors, True, False)
    for bullet, hit_meteors in collisions.items():
        for meteor in hit_meteors:
            meteor.transform_to_cheese()

    for meteor in meteors:
        if pygame.sprite.collide_rect(player, meteor):
            if meteor.transformed:
                player.lives = min(player.lives + 1, 10)
                meteor.reset()
            else:
                player.lives -= 2
                meteor.reset()

    if player.lives <= 0:
        run = False
            
    # 3. Drawing
    # Draw Background FIRST
    scrolling_bg.draw(screen)
    
    # Draw Sprites SECOND
    all_sprites.draw(screen)
    
    # Draw UI (Lives) LAST
    draw_lives_in_words(screen, player.lives)
       
    # Flip display ONCE per frame
    pygame.display.flip()
    clock.tick(80)

pygame.quit()
