import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, image, size, speed, group):
        """
        it creates sprite player
        :param pos: player position
        :param image: image of our player
        :param size: size of player image
        :param group: what group will it be (commonly: camera group)
        :param speed: speed of a player
        """
        super().__init__(group)
        self.original_image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, size)
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.math.Vector2()
        self.speed = speed
        self.flip = 'right'

    def input(self):
        """
        detects in which way player should move
        :return:
        """
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            if self.flip == 'left':
                self.image = pygame.transform.flip(self.image, True, False)
            self.flip = 'right'
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            if self.flip == 'right':
                self.image = pygame.transform.flip(self.image, True, False)
            self.flip = 'left'
        else:
            self.direction.x = 0

    def update(self):
        """
        it should be redefined
        :return:
        """
        self.input()
        self.rect.center += self.direction * self.speed
