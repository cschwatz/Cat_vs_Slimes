import pygame
from settings import *

class Magic(pygame.sprite.Sprite):
    def __init__(self, groups, player, spell_type, direction):
        super().__init__(groups)
        #player
        self.player = player
        self.player_direction = direction.split('_')[0]
        #initialization
        self.import_magic_sprites()
        if spell_type == 'heal':
            self.was_cast = True
            self.is_active = False
        else:
            self.is_active = True
        #animation
        self.frame_index = 0
        self.animation_speed = 0.15
        self.spell = spell_type
        if self.spell == 'heal':
            self.image = self.magic_animations[self.spell]['start'][self.frame_index]
        else:
            self.image = self.magic_animations[self.spell]['moving'][self.frame_index]
        self.rect = self.image.get_rect(center=self.player.rect.center)
        #magic attributes
        self.spell_cooldown = magic_data[spell_type]['cooldown']
        self.cost = magic_data[spell_type]['cost']
        #sounds
        self.import_spell_sfx()

    def import_magic_sprites(self):
        self.magic_sprites = {
            'fire':{'moving':[(14,25,32,11), (59,24,35,11), (104,24,38,11), (150,24,40,12)], 'hit':[(14,5,27,37), (58,3,32,40), (105,3,32,40), (164,3,21,35), (222,3,13,28)]},
            'wind':{'moving':[(7,3,18,26), (39,5,18,22), (72,6,17,20), (7,37,18,22), (39,35,18,26), (71,31,18,32)], 'hit':[(5,4,18,23), (37,4,24,23), (73,4,22,23), (13,39,19,20)]},
            'ice':{'moving':[(10,12,25,9), (58,12,25,9), (106,12,25,9), (154,12,25,9)], 'hit':[(11,3,27,24), (65,3,23,25), (113,3,28,28), (160,2,30,30), (208,2,31,30), (263,2,24,23)]},
            'heal':{'start':[(19,23,66,24), (106,10,78,54), (200,14,72,54), (294,27,63,30)], 'moving':[(26,31,31,26), (85,13,26,50), (133,17,28,38), (178,24,26,24), (213,31,22,10)]}
        }
        self.magic_animations = {
            'fire':{'moving':[], 'hit':[]},
            'wind':{'moving':[], 'hit':[]},
            'ice':{'moving':[], 'hit':[]},
            'heal':{'start':[], 'moving':[]}
        }

        for spell in self.magic_sprites.keys():
            for frame_type in self.magic_sprites[spell].keys():
                if frame_type:
                    for frame in self.magic_sprites[spell][frame_type]:
                        if spell == 'heal':
                            self.magic_animations[spell][frame_type].append(self.load_sprite(f'sprites/magic/magic_{spell}/{frame_type}.png', frame, 0.8, (255,255,255)))
                        else:
                            image = self.load_sprite(f'sprites/magic/magic_{spell}/{frame_type}.png', frame, 2, (255,255,255))
                            transformed_image = self.get_player_facing_position(image, self.player_direction)                           
                            self.magic_animations[spell][frame_type].append(transformed_image)
    
    def import_spell_sfx(self):
        self.spell_sounds = {
            'fire': {'moving': pygame.mixer.Sound('sounds/fire_move.wav'), 'hit': pygame.mixer.Sound('sounds/fire_hit.wav')},
            'ice': {'moving': pygame.mixer.Sound('sounds/ice_move.wav'), 'hit': pygame.mixer.Sound('sounds/ice_hit.wav')},
            'wind':{'moving': pygame.mixer.Sound('sounds/wind_move.wav'), 'hit': pygame.mixer.Sound('sounds/wind_hit.wav')},
            'heal': pygame.mixer.Sound('sounds/heal.wav')
        }

    def get_player_facing_position(self, image, direction): #gets player position/direction to know where to spawn the spell (when spell is cast)
        if direction == 'left':
            return pygame.transform.flip(image, True, False).convert_alpha()
        elif direction == 'up':
            return pygame.transform.rotate(image, 90).convert_alpha()
        elif direction == 'down':
            return pygame.transform.rotate(image, 270).convert_alpha()
        else:
            return image

    def load_sprite(self, filename, frame, scale=None, color=None): #helper function to load an image (surface) by passing a sprite sheet and coordinates to extract a subsurface of the given spritesheet
        spritesheet = pygame.image.load(filename) #get the spritesheet
        image = spritesheet.subsurface(pygame.Rect(frame)) #extract a subsurface of the spritesheet by giving a coordinate (Rect) -> tuple (x, y, width, height)
        image = pygame.transform.scale(image, (frame[2] * scale, frame[3] * scale)) # get width and height from the frame (tuple) and scale them based on a given scale factor given
        image.set_colorkey(color) #removes background colour (colour is passed as argument) of the surface -- makes the png have a transparent background so it does not look weird on the game
        return image
    
    def mana_cost(self):
        if self.player.mana >= self.cost:
            self.player.mana -= self.cost
            return True
        else:
            return False

    def animate(self):
            if self.is_active:
            #loop over frames
                self.frame_index += self.animation_speed
                if self.frame_index >= len(self.magic_animations[self.spell]['moving']):
                    self.frame_index = 0
                    if self.spell == 'heal':
                        self.kill()
                self.image = self.magic_animations[self.spell]['moving'][int(self.frame_index)]
                self.rect = self.image.get_rect(topleft=self.hitbox.topleft)

class Projectile(Magic):
    def __init__(self, groups, player, direction, player_rect, player_pos, spell, obstacle_group, attackable_group):
        super().__init__(groups, player, spell, direction)
        #player
        self.player_direction = direction.split('_')[0] #passed in as argument from the player class -- gets the player status which has the following format str: 'direction_status'
        self.player_rect = player_rect
        self.player_pos = player_pos
        #spell animation
        self.spell = spell
        self.animation_speed = 0.25
        self.image = self.magic_animations[self.spell]['moving'][self.frame_index]
        self.rect = self.image.get_rect()
        self.adjust_spell_initial_rect(self.player_direction) #gets image.rect based on the direction the player is facing and also transforms (rotate/flip) the spell sprite based on the direction the player is facing
        self.hitbox = self.rect
        self.has_collided = False
        #movement
        self.projectile_direction = pygame.math.Vector2()
        self.projectile_velocity = 5
        self.maximum_distance = 300 #maximum distance that the projectile can travell before disappearing
        self.can_move = True
        #collision
        self.attackable_group = attackable_group
        self.obstacle_group = obstacle_group
        #sound
        self.spell_sound_moving = self.spell_sounds[self.spell]['moving']
        self.spell_sound_moving.set_volume(0.5)
        self.spell_sound_moving.play()
        self.spell_sound_hit = self.spell_sounds[self.spell]['hit']
        self.spell_sound_hit.set_volume(0.4)

    def adjust_spell_initial_rect(self, direction): #gets player position/direction to know where to spawn the spell (when spell is cast)
        if direction == 'right':
            self.rect = self.image.get_rect(midleft=self.player_rect.midright + pygame.math.Vector2(0,2))
        elif direction == 'left':
            self.rect =  self.image.get_rect(midright=self.player_rect.midleft + pygame.math.Vector2(0,2))
        elif direction == 'up':
            self.rect =  self.image.get_rect(midbottom=self.player_rect.midtop)
        else:
            self.rect =  self.image.get_rect(midtop=self.player_rect.midbottom)

    def move_projectile(self):
        if self.player_direction == 'right':
            self.hitbox.x += self.projectile_velocity
        elif self.player_direction == 'left':
            self.hitbox.x -= self.projectile_velocity
        elif self.player_direction == 'up':
            self.hitbox.y -= self.projectile_velocity
        else:
            self.hitbox.y += self.projectile_velocity

    def travelled_distance(self):
        player_vector = pygame.math.Vector2(self.player_pos)
        spell_vector = pygame.math.Vector2(self.hitbox.x, self.hitbox.y)
        travelled_distance = (player_vector - spell_vector).magnitude() #distance between the player and the projectile 
        return travelled_distance

    def destroy_projectile(self):
        if int(self.travelled_distance()) > self.maximum_distance or self.has_collided:
            self.play_projectile_end_animation()

    def check_projectile_collision(self):
        for sprite in self.obstacle_group:
            if sprite.hitbox.colliderect(self.hitbox):
                self.has_collided = True
        for sprite in self.attackable_group:
            if sprite.hitbox.colliderect(self.hitbox):
                self.has_collided = True

    def play_projectile_end_animation(self):
        self.can_move = False
        self.spell_sound_hit.play()
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.magic_animations[self.spell]['hit']):
                self.frame_index = 0
                self.kill()
        self.image = self.magic_animations[self.spell]['hit'][int(self.frame_index)]
        self.rect = self.image.get_rect(topleft=self.hitbox.topleft)
        if self.spell == 'fire':
            if self.player_direction in ['right', 'left']:
                self.rect.y -= 30
            else:
                self.rect.x -= 15

    def animate_projectile(self):
        if not int(self.travelled_distance()) > self.maximum_distance and not self.has_collided:
            self.animate()

    def update(self):
        if self.can_move:
            self.move_projectile()
        self.check_projectile_collision()
        self.destroy_projectile()
        if self.alive():
            self.animate_projectile()

class Heal(Magic):
    def __init__(self, groups, player, spell_type, player_direction):
        super().__init__(groups, player, spell_type, player_direction)
        self.rect = self.player.rect
        self.hitbox = self.player.hitbox
        self.can_be_healed = True
        #sound
        self.heal_sound = self.spell_sounds['heal']
        self.heal_sound.set_volume(0.5)
        self.heal_sound.play()

    def heal_player(self):
        if self.was_cast:
            self.player.health += magic_data['heal']['amount']
            if self.player.health >= self.player.stats['health']:
                self.player.health = self.player.stats['health']
            self.can_be_healed = False
    
    def animate(self): #since the heal animation comes from a different spritesheet, we need to make some changes to the animation method
            if self.was_cast:
                self.frame_index += 0.15
                if self.frame_index >= len(self.magic_animations[self.spell]['start']):
                    self.frame_index = 0
                    self.was_cast = False
                    self.is_active = True
                self.image = self.magic_animations[self.spell]['start'][int(self.frame_index)]
                self.rect = self.image.get_rect(topleft=self.hitbox.topleft)
                self.rect.x -= 13
                self.rect.y += 5
            
            if self.is_active:
            #loop over frames
                self.frame_index += 0.15
                if self.frame_index >= len(self.magic_animations[self.spell]['moving']):
                    self.frame_index = 0
                    if self.spell == 'heal':
                        self.kill()
                self.image = self.magic_animations[self.spell]['moving'][int(self.frame_index)]
                self.rect = self.image.get_rect(topleft=self.hitbox.topleft)
                self.rect.y -= 50

    def update(self):
        if self.can_be_healed:
            self.heal_player()
        self.animate()