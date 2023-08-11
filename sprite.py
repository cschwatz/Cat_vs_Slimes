import pygame
from settings import *

#classes to handle different Tiles/Objects that are imported to the game

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)

class Barrier(pygame.sprite.Sprite): #barrier are invisible Tiles that have the purpose of blocking the player from moving to "unwanted" zones
    def __init__(self, pos, surf, groups, name):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.offset_x = OFFSET_VALUE[name][0]
        self.offset_y = OFFSET_VALUE[name][1]
        self.hitbox = self.rect.inflate(self.offset_x, self.offset_y) #for collision detection

class Assets(pygame.sprite.Sprite): #assets that are placed above the floor tiles
    def __init__(self, pos, surf, groups, name):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.offset_y = OFFSET_VALUE[name]
        self.hitbox = self.rect.inflate(0, self.offset_y) #for collision detection


class Bush(pygame.sprite.Sprite): #only handle bushes
    def __init__(self, pos, surf, groups, name):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(bottomleft = pos)
        self.offset_y = OFFSET_VALUE[name]
        self.hitbox = self.rect.inflate(0, self.offset_y) #for collision detection


