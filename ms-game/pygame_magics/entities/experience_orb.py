import pygame


class ExperienceOrb(pygame.sprite.Sprite):
    def __init__(self, pos, image, size, group):
        """
        sprites of experience orbs
        :param pos: position
        :param image: its image
        :param size: its size
        :param group: group in what object is
        """
        super().__init__(group)
        self.original_image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, size)
        self.rect = self.image.get_rect()
        self.rect.center = pos
