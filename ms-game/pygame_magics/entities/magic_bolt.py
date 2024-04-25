from math import degrees, cos, sin, atan2, pi

import pygame


class MagicBoltBullet(pygame.sprite.Sprite):
    def __init__(self, pos, image, angle, damage, size, speed, delay, group):
        """
        fires a bullet
        :param pos: position of player
        :param image: image of bullet
        :param angle: angle in which it fires
        :param damage: amount of damage
        :param size: bullet size
        :param speed: bullet speed
        :param delay: delay in time
        :param group: group of all bullets
        """
        super().__init__(group)
        self.original_image = (pygame.image.load(image).
                               convert_alpha())
        orig_size = self.original_image.get_size()
        self.image = pygame.transform.scale(pygame.transform.rotate(self.original_image, degrees(2 * pi - angle)),
                                            (orig_size[0] * size, orig_size[1] * size))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.angle = 2 * pi - angle
        self.damage = damage
        self.velocity = speed
        self.t = 0
        self.delay = delay

    def update(self, enemies):
        if self.delay <= self.t:
            self.rect.centerx = self.rect.centerx + self.velocity * self.t * cos(-self.angle)
            self.rect.centery = self.rect.centery - self.velocity * self.t * sin(self.angle)
        self.t += 1

        for enemy in enemies.sprites():
            if pygame.sprite.collide_rect(self, enemy):
                enemy.lost_hp(self.damage)
                if enemy.hp <= 0:
                    enemy.remove()
                    enemy.kill()


class MagicBolt:
    def __init__(self, player_pos, image):
        """
        :param player_pos: player position
        :param bullet_image: bullet image
        """
        self.player_pos = player_pos
        self.image = image

    def spawn_magic_bolt(self, magic_bolt_group, player_pos, n, nearest_enemy_func):
        """
        :param magic_bolt_group: Sprite Group for magic bolt
        :param player: player position
        :param n: level of magic bolt
        :param nearest_enemy_func: function which will give example of nearest enemy
        :return:
        """
        amount = 1
        damage = 10
        size = 1
        speed = 1
        if n >= 2:
            amount += 1
        if n >= 3:
            damage = damage * 1.3
        if n >= 4:
            damage = damage * 1.8
            size = 1.8 * size
            speed = 1.8 * speed
        if n >= 5:
            amount += 1
        if n >= 6:
            damage = damage * 1.5
        if n >= 7:
            damage = damage * 1.7
            size = 1.5 * size
        for j in range(amount):
            enemy_rect = nearest_enemy_func()
            if enemy_rect:
                enemy_rect = enemy_rect.rect.center
                angle = atan2((enemy_rect[1] - player_pos[1]), (enemy_rect[0] - player_pos[0]))
                delay = 20 * j
                MagicBoltBullet(self.player_pos, self.image, angle, damage, size, speed, delay, magic_bolt_group)

    def stop_fire(self, magic_bolt_group, enemies):
        """
        deletes all instances of class
        :param magic_bolt_group: magic bolt group
        :param enemies: enemy group
        :return:
        """
        for sprite in magic_bolt_group.sprites():
            sprite.remove()
            sprite.kill()
            sprite.update(enemies)

    def update(self, player_position, magic_bolt_group, n, nearest_enemy):
        """
        you should implement something new here
        :param player_position: player position
        :param magic_bolt_group: magic bolt group
        :param n: level of the weapon
        :param nearest_enemy: function which finds nearest enemy
        :return:
        """
        self.player_pos = player_position
        self.spawn_magic_bolt(magic_bolt_group, player_position, n, nearest_enemy)

