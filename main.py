import pygame
import random
from pygame import mixer
import os 

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

mixer.music.load(fr'{mydir}/Music/tune_1.mp3')
mixer.music.set_volume(0.03)
mixer.music.play(loops=-1)

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

# Load and scale images
BACKGROUND_IMG = pygame.image.load(fr"{mydir}/Images/Background.png") # noqa: F541
BACKGROUND_IMG = pygame.transform.scale(BACKGROUND_IMG, (SCREEN_WIDTH, SCREEN_HEIGHT))

BACKGROUND_IMG_GAME_OVER = pygame.image.load(fr"{mydir}/Images/Cheese.png") # noqa: F541
BACKGROUND_IMG_GAME_OVER = pygame.transform.scale(BACKGROUND_IMG, (SCREEN_WIDTH, SCREEN_HEIGHT))

player_image_left = pygame.image.load(fr'{mydir}/Images/Player.Left.png')  # noqa: F541
player_image_left = pygame.transform.scale(player_image_left, (player_width, player_height))

player_image_right = pygame.image.load(fr'{mydir}/Images/Player.Right.png')  # noqa: F541
player_image_right = pygame.transform.scale(player_image_right, (player_width, player_height))

player_image_default = pygame.image.load(fr'{mydir}/Images/Player.png')  # noqa: F541
player_image_default = pygame.transform.scale(player_image_default, (player_width, player_height))

player_image = player_image_default  # Default image

meteor_image = pygame.image.load(fr'{mydir}/Images/Meteor.png') # noqa: F541
meteor_image = pygame.transform.scale(meteor_image, (object_width, object_height))

cheese_image = pygame.image.load(fr'{mydir}/Images/Cheese.png') # noqa: F541
cheese_image = pygame.transform.scale(cheese_image, (object_width, object_height))

b_imgs = [pygame.image.load(fr'{mydir}/Images/Bullet-Red.png'), pygame.image.load(fr'{mydir}/Images/Bullet-Green.png')]  # noqa: F541

bullet_image = random.choice(b_imgs)
bullet_image = pygame.transform.scale(bullet_image, (20, 30))

# Player class
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
        if keys[pygame.K_a] or keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.image = player_image_left  # Change image when 'a' is pressed
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
            self.image = player_image_right  # Change image when 'd' is pressed
        else:
            self.image = player_image_default  # Default image when no key is pressed

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

    def draw(self):
        screen.blit(self.image, self.rect.topleft)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        # Remove the bullet if it goes off-screen
        if self.rect.bottom < 0:
            self.kill()

# Meteor class
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

# Create objects without overlap
meteors = pygame.sprite.Group()
for _ in range(7):
    meteor = Meteor(random.randint(0, SCREEN_WIDTH - object_width), random.randint(-SCREEN_HEIGHT // 2, 0))
    meteors.add(meteor)

# Background function
def BG():
    # Blit the background image 
    screen.blit(BACKGROUND_IMG, (0, 0))
    all_sprites.draw(screen)
    pygame.display.update()

# Convert lives to words
def lives_to_words(lives):
    words = {
        10: "10 Lives",
        9: "9 Lives",
        8: "8 Lives",
        7: "7 Lives",
        6: "6 Lives",
        5: "5 Lives",
        4: "4 Lives",
        3: "3 Lives",
        2: "2 Lives",
        1: "1 Life",
        0: "0 Lives"
    }
    return words.get(lives, "")

# Draw lives in words
def draw_lives_in_words(screen, lives):
    font = pygame.font.SysFont(None, 36)
    lives_text = font.render(f'Lives: {lives_to_words(lives)}', True, WHITE)
    screen.blit(lives_text, (10, 10))

# Main game loop
pygame.time.delay(1000)
clock = pygame.time.Clock()
player = Player()
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()

all_sprites.add(player)
all_sprites.add(meteors)

run = True

# Initialise lives
draw_lives_in_words(screen, player.lives)

while run:
    bullet_image = random.choice(b_imgs)
    bullet_image = pygame.transform.scale(bullet_image, (20, 30))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                # Create a new bullet when 'S' is pressed
                bullet = Bullet(player.rect.centerx, player.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            elif event.key == pygame.K_DOWN:
                # Create a new bullet when 'Down Arrow' is pressed
                bullet = Bullet(player.rect.centerx, player.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)    

    # Check for collisions between bullets and meteors
    collisions = pygame.sprite.groupcollide(bullets, meteors, True, False)
    for bullet, hit_meteors in collisions.items():
        for meteor in hit_meteors:
            meteor.transform_to_cheese()

    # Check for player collision with meteors (ignore cheese)
    for meteor in meteors:
        if pygame.sprite.collide_rect(player, meteor):
            if meteor.transformed:
                # Restore half a life if player collides with cheese
                player.lives = min(player.lives + 1, 10)
                meteor.reset()
            else:
                # Lose two lifes if player collides with a meteor
                player.lives -= 2
                meteor.reset()

                # Update lives
                draw_lives_in_words(screen, player.lives)

    # Check for game over
    if player.lives <= 0:
        run = False
            

    # Update all sprites
    all_sprites.update()
        
    # Draw background
    BG()
        
    pygame.display.flip()
    clock.tick(60)


pygame.quit()

