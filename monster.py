import pygame
from math import sin
from settings import *


class Monster(pygame.sprite.Sprite):
    def __init__(self, pos, slime, groups, player, obstacle_sprites):
        super().__init__(groups)
        #sprites
        self.import_assets()
        self.pos = pos
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect
        self.x = pos[0]
        self.y = pos[1]
        #movement
        self.direction = pygame.math.Vector2()
        self.player = player # to be used in methods that require the player's position or hitbox
        self.direction_of_movement = 'front'
        self.obstacle_sprites = obstacle_sprites # for collision detection with map assets
        #animation
        self.animation_speed = 0.15
        self.frame_index = 0
        self.slime = slime
        self.is_alive = True
        self.can_move = True
        #stats
        self.status = 'idle'
        self.velocity = monster_data[slime]['speed']
        self.notice_radius = monster_data[slime]['notice_radius']
        self.attack_radius = monster_data[slime]['attack_radius']
        self.max_health = monster_data[slime]['health']
        self.health = monster_data[slime]['health']
        self.exp = monster_data[slime]['exp']
        self.damage = monster_data[slime]['damage']
        self.resistance = monster_data[slime]['resistance']
        #handling damage taken
        self.is_vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 700
        self.pushback = 3
        self.can_be_pushbacked = True
        self.pushback_time = 300
        #sounds
        self.player_hurt_sound = pygame.mixer.Sound('sounds/player_take_damage.wav')
        self.player_hurt_sound.set_volume(0.5)
        self.slime_move_sound = pygame.mixer.Sound('sounds/slime_move.wav')
        self.slime_move_sound.set_volume(0.3)
        self.slime_move_sound_cooldown = 50
        self.death_sound = pygame.mixer.Sound('sounds/slime_death.wav')
        self.death_sound.set_volume(0.5)

    def get_player_distance_and_direction(self):
        slime_vector = pygame.math.Vector2(self.rect.center)
        player_vector = pygame.math.Vector2(self.player.rect.center)
        distance = (player_vector - slime_vector).magnitude() #magnitude represents the length of the vector -- thus, will give us the distance between the slime and the player
        if distance > 0:
            direction = (player_vector - slime_vector).normalize() #by normalizing the vector, we get a vetor of length 1 -- because we only want the direction of the vector, not it's length (magnitude) -- this way, the slime knows which direction to go to the player
        else:
            direction = pygame.math.Vector2() #enemy is on top of player -- vector is then (0, 0)

        return (distance, direction)

    def get_status(self): #see if monster should be chasing player or idle
        distance = self.get_player_distance_and_direction()[0] #tuple (distance, direction)
        if distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'

    def get_direction_of_movement(self, direction): #helper function to know which direction of the sprite should be animated
        if direction == 'up':
            return 'front'
        else: 
            return 'back'
    
    def move(self):
        if self.direction.magnitude() != 0: # if vector is something else than (0,0) -- normalize it to just get the direction of the vector
            self.direction = self.direction.normalize()
        if self.status == 'move':
            self.direction = self.get_player_distance_and_direction()[1]
            if self.direction.y > 0:
                self.direction_of_movement = self.get_direction_of_movement('up')
            else:
                self.direction_of_movement = self.get_direction_of_movement('down')
            #apply movement to the hitbox first and then apply to rect
            self.hitbox.x += self.direction.x * self.velocity
            self.collision('horizontal')
            self.hitbox.y += self.direction.y * self.velocity
            self.collision('vertical')
            self.rect.center = self.hitbox.center
        else:
            self.direction = pygame.math.Vector2()

    def damage_player(self): #calculates the damage that is dealt to the player
        if self.player.is_vulnerable:
            self.player.health -= self.damage - self.player.stats['defense'] #reduces the monster's damage based on the player's resistance stat
            self.player.is_vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.player_hurt_sound.play()

    def take_damage(self): #method to reduce monster's health based on players damage
        if self.is_vulnerable:
            self.health -= self.player.get_player_total_damage()
            self.check_death()
            self.hurt_time = pygame.time.get_ticks()
            self.is_vulnerable = False

    def cooldowns(self): #handles i-frames
        current_time = pygame.time.get_ticks()
        if not self.is_vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.is_vulnerable = True

    def push_back_after_damage(self): #method that gives the monster a little "knockback" when it takes damage
        if not self.is_vulnerable and self.pushback_time:
            self.direction *= -self.pushback
            self.hitbox.x += self.direction.x
            self.collision('horizontal')
            self.hitbox.y += self.direction.y
            self.collision('vertical')

    def check_death(self):
        if self.health <= 0:
            self.frame_index = 0
            self.is_alive = False
            self.give_player_exp()
            self.death_sound.play()

    def give_player_exp(self):
        self.player.exp += self.exp

    def collision(self, direction): #checks collision with map assets/objects
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom

    def import_assets(self):
        sprite_sheets = {
            'blue': {'back': [(10, 5, 12, 11), (10, 23, 12,11), (11, 34, 10, 11), (10, 52, 12, 11), (10, 69, 12, 11), (9, 85, 12, 11), (9,101,14,11)], 'front': [(10, 5, 12, 11), (10,21,12,11), (11,34,10,11), (10,52,12,11),(10,69,12,11),(10,85,12,11), (9,101,14,11)], 'death': [(9,10,13,15),(40,8,14,16),(72,11,17,16),(104,10,17,16)]},
            'green': {'back': [(10, 5, 12, 11), (10, 21, 12,11), (11, 33, 10, 12), (10, 51, 12, 12), (10, 68, 12, 12), (9, 84, 12, 12), (9,100,14,12)], 'front': [(10, 5, 12, 11), (10,21,12,11), (11,34,10,11), (10,52,12,11),(10,69,12,11),(10,85,12,11), (9,101,14,11)], 'death': [(10,40,12,15),(40,38,14,16),(72,41,17,16),(104,41,17,16)]},
            'pink': {'back': [(10, 5, 12, 11), (10, 23, 12,11), (11, 34, 10, 11), (10, 52, 12, 11), (10, 69, 12, 11), (9, 85, 12, 11), (9,101,14,11)], 'front': [(10, 5, 12, 11), (10,21,12,11), (11,34,10,11), (10,52,12,11),(10,69,12,11),(10,85,12,11), (9,101,14,11)], 'death': [(11,74,12,15),(41,72,14,16),(73,73,17,16),(105,76,17,16)]},
            'purple': {'back': [(10, 5, 12, 11), (10, 23, 12,11), (11, 34, 10, 11), (10, 52, 12, 11), (10, 69, 12, 11), (9, 85, 12, 11), (9,101,14,11)], 'front': [(10, 5, 12, 11), (10,21,12,11), (11,34,10,11), (10,52,12,11),(10,69,12,11),(10,85,12,11), (9,101,14,11)], 'death': [(13,106,12,15),(43,104,14,16),(75,106,17,16),(107,107,17,16)]}
        }

        self.animations = {
            'blue': {'back': [], 'front': [], 'death': []},
            'green': {'back': [], 'front': [], 'death': []},
            'pink': {'back': [], 'front': [], 'death': []},
            'purple': {'back': [], 'front': [], 'death': []}
        }

        for slime in sprite_sheets.keys():
            for direction in sprite_sheets[slime].keys():
                if sprite_sheets[slime][direction]:
                    for frame in sprite_sheets[slime][direction]:
                        if direction == 'front' or direction == 'back':
                            self.animations[slime][direction].append(self.load_sprite(f'sprites/monsters/{slime}_{direction}.png', frame, 4, (255, 255, 255)))
                        else:
                            self.animations[slime][direction].append(self.load_sprite('sprites/monsters/death_animation_slimes.png', frame, 3, (255, 255, 255)))

    def load_sprite(self, filename, frame, scale=None, color=None): #helper function to load an image (surface) by passing a sprite sheet and coordinates to extract a subsurface of the given spritesheet
        self.spritesheet = pygame.image.load(filename) #get the spritesheet
        self.image = self.spritesheet.subsurface(pygame.Rect(frame)) #extract a subsurface of the spritesheet by giving a coordinate (Rect) -> tuple (x, y, width, height)
        self.image = pygame.transform.scale(self.image, (frame[2] * scale, frame[3] * scale)) # get width and height from the frame (tuple) and scale them based on a given scale factor given
        self.image.set_colorkey(color) #removes background colour (colour is passed as argument) of the surface -- makes the png have a transparent background so it does not look weird on the game
        return self.image

    def play_death_animation(self):
        self.animation_speed = 0.1
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animations[self.slime]['death']):
            self.frame_index = 0
            self.kill()
        self.image = self.animations[self.slime]['death'][int(self.frame_index)]
        self.rect = self.image.get_rect(bottomleft = self.hitbox.center)

    def play_slime_moving_sound(self): #it is a repeating sound, so we use a helper method
        
        self.slime_move_sound_cooldown -= 1
        if self.slime_move_sound_cooldown <= 0:
            self.slime_move_sound_cooldown = 50
            self.slime_move_sound.play()

    def wave_value(self): #helper function to achieve "blinking" animation when taking damage
        value = sin(pygame.time.get_ticks())
        if value >= 0: 
            return 255
        else: 
            return 0

    def animate(self):
        self.frame_index += self.animation_speed
        #loop over frames
        if self.frame_index >= len(self.animations[self.slime][self.direction_of_movement]):
            self.frame_index = 0
        self.image = self.animations[self.slime][self.direction_of_movement][int(self.frame_index)]
        self.rect = self.image.get_rect(bottomleft = self.hitbox.bottomleft)

        if not self.is_vulnerable:
            alpha_value = self.wave_value()
            self.image.set_alpha(alpha_value)
        else:
            self.image.set_alpha(255)

    def update(self):
        self.push_back_after_damage()
        if self.is_alive:
            self.animate()
        else:
            self.play_death_animation()
        self.get_status()
        self.move()
        self.cooldowns()
        if self.status == 'move':
            self.play_slime_moving_sound()