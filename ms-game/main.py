import ctypes
import random
import sqlite3
import sys
from math import sqrt

import pygame
from pygame_magics.camera.camera import CameraGroup
from pygame_magics.entities import enemy
from pygame_magics.entities import player
from pygame_magics.entities import experience_orb
from pygame_magics.entities import magic_bolt
from pygame_magics.entities import singleton

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='logs/game.log',
    encoding='utf-8',
    level=logging.DEBUG,
    format='%(levelname)s:%(message)s'
)


class PlayerStats(metaclass=singleton.Singleton):

    def __init__(self):
        """
        player characteristics
        """
        self.health = 100
        self.player = None
        self.oil = 0
        self.amount_of_oil = 0
        self.experience = 0
        self.n = 1
        self.play_time = 0

    def check_experience(self):
        """
        here we check if we come on a new weapon level then we promote
        :return:
        """
        if self.experience_growth() <= self.experience:
            self.experience = 0
            self.n += 1

    def experience_growth(self):
        """
        function type of new_cost = base_cost * (rate^level)
        :return:
        """
        return 10 * (1.57 ** (self.n - 1))


class Settings(metaclass=singleton.Singleton):

    def __init__(self):
        """
        here are some setting of my game
        """
        self.map_x = 2800 * 5
        self.map_y = 1300 * 5
        self.FPS = 60
        self.game_works = True
        self.status = "Not finished"
        self.range_amount_of_cisterns = (5, 9)


class Enemy(enemy.Enemy):
    def __init__(self, pos, image, image_size, speed, health, group):
        """
        inherited from base class enemy
        :param pos: (int, int)
        :param image: str
        :param image_size: (int, int)
        :param speed: int speed value pixels per frame
        :param health: int
        :param group: pygame.sprite.Group
        """
        super().__init__(pos, image, image_size, speed, health, group)

    def update(self, player):
        """
        damaging player and movement of alien
        :param player: pygame.sprite.Sprite
        :return:
        """
        direction_vector = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(self.rect.center)
        direction_vector.normalize_ip()
        self.rect.move_ip(direction_vector * self.speed)
        if pygame.sprite.collide_rect(self, player):
            PlayerStats().health -= 10


class Rocket(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        """
        sprite of rocket to go to next level
        :param pos: (int, int) rocket position
        :param group: pygame.sprite.Group rocket group
        """
        super().__init__(group)
        self.original_image = pygame.image.load("graphics/rocket/rocket.png").convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (self.original_image.get_width() * 0.5,
                                                                  self.original_image.get_height() * 0.5))
        self.rect = self.image.get_rect()
        self.rect.center = pos


class Oil(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        """
        sprite of oil to go to next level
        :param pos: (int, int) oil bucket position
        :param group: pygame.sprite.Group oil group
        """
        super().__init__(group)
        self.original_image = pygame.image.load("graphics/carbons/oil.png").convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.center = pos


class SpriteGroups(metaclass=singleton.Singleton):
    def __init__(self):
        """
        this class contains all sprite groups
        """
        self.camera = CameraGroup(Settings().map_x, Settings().map_y, "graphics/mars_photogrammetry/map.png", 12)
        self.oil_group = pygame.sprite.Group()
        self.experience_orb_group = pygame.sprite.Group()
        self.rocket_group = pygame.sprite.Group()
        self.experience_experience_orb_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.magic_bolt_group = pygame.sprite.Group()
        self.magic_bolt = None


class Player(player.Player):
    def __init__(self, pos, image, size, speed, group):
        """
        this is the player class which I overwrote for this game logic
        :param pos: (int, int) position
        :param image: str image of a player
        :param size: (int, int) size of player
        :param speed: int our player speed
        :param group: pygame.sprite.Group
        """
        super().__init__(pos, image, size, speed, group)
        self.time_offset = 100
        self.last_time = 0
        self.state = 0

    def update(self):
        """
        here I implement movement + check collisions with subjects
        :return:
        """
        sprite_groups = SpriteGroups()
        self.input()
        self.rect.center += self.direction * self.speed

        collided_oil = pygame.sprite.spritecollideany(self, sprite_groups.oil_group)
        if collided_oil:
            SpriteGroups().oil_group.remove(collided_oil)
            collided_oil.kill()
            PlayerStats().oil += 1

        collided_orb = pygame.sprite.spritecollideany(self, sprite_groups.experience_orb_group)
        if collided_orb:
            sprite_groups.experience_orb_group.remove(collided_orb)
            collided_orb.kill()
            PlayerStats().experience += 1
            global total_amount
            total_amount -= 1

        keys = pygame.key.get_pressed()
        if pygame.sprite.spritecollideany(self, sprite_groups.rocket_group):
            if keys[pygame.K_RETURN]:
                if PlayerStats().oil == PlayerStats().amount_of_oil:
                    logging.debug("Mission accomplished. You returned on the Earth")
                else:
                    if PlayerStats().oil < PlayerStats().amount_of_oil:
                        logging.debug("Not enough oil")
                        Settings().game_works = False
                        Settings().status = ("While you were flying,\nfuel on rocket ended\nbefore you have"
                                             " reached\nOUR homeland-planet\nEarth")


def spawn_orbs(amount):
    """
    this function spawns orbs
    :param amount: int (amount of orbs on map)
    :return:
    """
    global total_amount
    for _ in range(amount):
        experience_orb.ExperienceOrb(
            (
                random.randint(-Settings().map_x, Settings().map_x),
                random.randint(-Settings().map_y, Settings().map_y)),
            "graphics/experience_orb/experience.png",
            (40, 40),
            SpriteGroups().experience_orb_group
        )
    total_amount = amount


def create_enemy():
    """
    this function creates enemies on map
    :return:
    """
    Enemy((PlayerStats().player.rect.center + pygame.math.Vector2(
        (-1) ** random.randint(1, 2) * screen.get_width(),
        (-1) ** random.randint(1, 2) * screen.get_height(),
    )), "graphics/ufo/ui2_106.png", (80, 80), 15, 50, SpriteGroups().enemy_group)


def get_nearest_enemy():
    """
    this function returns sprite of nearest enemy to player
    :return:
    """
    arr = []
    player_x, player_y = PlayerStats().player.rect.center
    for enemy in SpriteGroups().enemy_group.sprites():
        delta = sqrt((enemy.rect.x - player_x) ** 2 + (enemy.rect.y - player_y) ** 2)
        arr.append((delta, enemy))
    return min(arr, key=lambda x: x[0])[1] if arr else 0


def draw_text(text, color, x, y):
    """
    this function draws text
    :param text: str
    :param color: color of a text
    :param x: int coordinate of label
    :param y: int coordinate of label
    :return:
    """
    font = pygame.font.SysFont("monospace", 25, bold=True)
    text_obj = font.render(text, 1, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    screen.blit(text_obj, text_rect)


pygame.init()

screen = pygame.display.set_mode((450, 270))
running = True
info_running = False
change_info = True
COLOR = "#002C35"
while running:
    if not info_running:
        if change_info:
            screen = pygame.display.set_mode((450, 270))
            change_info = False
        screen.fill(COLOR)
        bg = pygame.image.load('graphics/mars_photogrammetry/mars.png')
        screen.blit(bg, (0, 0))
        draw_text("Start Game", COLOR, 65, 60)
        draw_text("Info", COLOR, 65, 100)
        start_button = pygame.Rect(65, 60, 300, 40)
        info_button = pygame.Rect(65, 100, 300, 40)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if start_button.collidepoint(mouse_pos):
                    logger.debug('Started game')
                    running = False
                if info_button.collidepoint(mouse_pos):
                    logger.debug('Info')
                    info_running = True
                    change_info = True
    else:
        if change_info:
            screen = pygame.display.set_mode((700, 600))
            change_info = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    info_running = False
                    change_info = True
        screen.fill(COLOR)
        COLOR_INFO = "#FFFFFF"
        bg = pygame.image.load('graphics/end-screen/info.jpg')
        screen.blit(bg, (0, 0))
        with open('info.txt') as f:
            sentence = f.readlines()
        screen.blit(screen, screen.get_rect())
        start_interspace = 100
        interspace = 0
        for part in sentence:
            draw_text(part.strip(), COLOR_INFO, 30, start_interspace + interspace)
            interspace += 30
    pygame.display.update()


def set_window_position():
    """
    redacts where window
    :return:
    """
    window_pos_x = 200
    window_pos_y = 100
    user32 = ctypes.windll.user32
    h_wnd = pygame.display.get_wm_info()["window"]
    user32.SetWindowPos(h_wnd, 0, window_pos_x, window_pos_y, 0, 0, 0x0001)


class Database:

    def __init__(self):
        self.base = sqlite3.connect('database.db')
        self.cur = self.base.cursor()
        self.create_table_time()

    def create_table_time(self):
        self.base.execute('CREATE TABLE IF NOT EXISTS {}(time text, time_int integer)'.format('best_time'))
        self.base.commit()

    def add_best_time(self, time, time_int):
        self.cur.execute('INSERT INTO best_time VALUES (?, ?)', (time, time_int))
        self.base.commit()

    def best_time(self):
        info = self.cur.execute('SELECT * FROM best_time').fetchall()
        if info:
            return min(info, key=lambda x: x[1])[0]
        else:
            return 'N/A'


set_window_position()
screen = pygame.display.set_mode((1280, 720))

pygame.mixer.music.load("music/38609_ng.mp3")
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(-1)

pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

sprites = SpriteGroups()
player = Player((screen.get_width() // 2, screen.get_height() // 2),
                "graphics/engineer/engineer_0_0.png", (100, 100), 25, sprites.camera)
PlayerStats().player = player

magic_bolt = magic_bolt.MagicBolt(PlayerStats().player.rect.center,
                                  "graphics/magic-bolt/bullet_ranger_init_weapon_xx8_1.png")
sprites.magic_bolt = magic_bolt

# amount of experience orbs on map
total_amount = 800

# total amount of experience orbs
normal_amount = total_amount

# amount of oil cisterns
amount_of_oil = random.randint(Settings().range_amount_of_cisterns[0], Settings().range_amount_of_cisterns[1])

# timers
enemy_timer = 0
magic_bolt_timer = 0

# enemy spawn interval function
SPAWN_RATE = 0.99
ENEMY_SPRITE_INTERVAL_FUNCTION = lambda time: SPAWN_RATE ** (time // 1000) * 3000

# fire interval of weapon
MAGIC_BOLT_FIRE_INTERVAL = 1000
MAGIC_BOLT_FIRE_SPEED = 200

# spawns all orbs on map
spawn_orbs(normal_amount)

PlayerStats().amount_of_oil = amount_of_oil

for i in range(amount_of_oil):
    rnd_x = random.randint(-Settings().map_x, Settings().map_x)
    rnd_y = random.randint(-Settings().map_y, Settings().map_y)
    Oil((rnd_x, rnd_y), sprites.oil_group)

Rocket((0, 0), sprites.rocket_group)
while True and Settings().game_works:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
    screen.fill("#c19a6b")
    current_time = pygame.time.get_ticks()
    if current_time - enemy_timer > ENEMY_SPRITE_INTERVAL_FUNCTION(current_time):
        create_enemy()
        enemy_timer = current_time
    sprites.camera.custom_draw(
        PlayerStats().player,
        sprites.oil_group,
        sprites.experience_orb_group,
        sprites.rocket_group,
        sprites.enemy_group,
        sprites.magic_bolt_group
    )
    sprites.enemy_group.update(PlayerStats().player)
    sprites.experience_orb_group.update()
    sprites.oil_group.update()
    sprites.magic_bolt_group.update(sprites.enemy_group)
    if PlayerStats().health <= 0:
        logging.debug('You dead')
        Settings().game_works = False
        Settings().status = "Mission failed.\nYou died on Mars"
        break
    PlayerStats().check_experience()
    PlayerStats().player.update()
    if current_time - magic_bolt_timer > MAGIC_BOLT_FIRE_SPEED:
        sprites.magic_bolt.update(PlayerStats().player.rect.center,
                                  sprites.magic_bolt_group,
                                  PlayerStats().n, get_nearest_enemy)
        magic_bolt_timer = current_time
    if current_time - magic_bolt_timer > MAGIC_BOLT_FIRE_INTERVAL:
        sprites.magic_bolt.stop_fire(sprites.magic_bolt_group, sprites.enemy_group)
    pygame.display.flip()
    if total_amount < normal_amount // 2:
        spawn_orbs(normal_amount // 2)
    PlayerStats().play_time = current_time
    pygame.display.update()
    clock.tick(Settings().FPS)

pygame.mixer.music.stop()
pygame.mouse.set_visible(True)
screen = pygame.display.set_mode((600, 350))


def create_play_time(seconds):
    if seconds // 60 == 0:
        return f'{seconds} s'
    elif seconds // (60 * 60) == 0:
        return f"{seconds // 60} min {seconds % 60} s"
    else:
        return f"{seconds // (60 * 60)} h {seconds % (60 * 60) // 60} min {seconds % (60 * 60) // (60 * 60)} s"


image_name = None
best_time = []

if Settings().status == "Mission accomplished.\nYou have returned on the Earth":
    image_name = 'graphics/end-screen/earth-cropped.jpg'
    color = (255, 0, 0)
    Database().add_best_time(create_play_time(PlayerStats().play_time // 1000), PlayerStats().play_time // 1000)
    best_time = [] + ['Your best:' + Database().best_time()]
else:
    image_name = 'graphics/end-screen/space.png'
    color = (255, 255, 0)
end_screen_surf = pygame.image.load(image_name)
end_screen_rect = end_screen_surf.get_rect()
my_font = pygame.font.SysFont("monospace", 25, bold=True)

status_sentence = (Settings().status.split('\n') + [] +
                   ['Play time:' + create_play_time(PlayerStats().play_time // 1000)] + best_time)
screen.blit(end_screen_surf, end_screen_rect)
start_interspace = 100
interspace = 0
for part in status_sentence:
    label = my_font.render(part, 1, color)
    screen.blit(label, (30, start_interspace + interspace))
    interspace += 30

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
    pygame.display.flip()
    pygame.display.update()
    clock.tick(Settings().FPS)
