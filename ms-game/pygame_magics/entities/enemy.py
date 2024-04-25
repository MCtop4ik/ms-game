import pygame


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, image, image_size, speed, health, group):
        super().__init__(group)
        self.original_image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, image_size)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.speed = speed
        self.hp = health

    def lost_hp(self, amount_hp):
        self.hp -= amount_hp

    def update(self, player):
        direction_vector = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(self.rect.center)
        direction_vector.normalize_ip()
        self.rect.move_ip(direction_vector * self.speed)
