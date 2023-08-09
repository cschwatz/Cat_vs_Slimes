import pygame
from math import sin
from settings import *
pygame.mixer.init()

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, obstacle_sprites, create_magic):
        super().__init__(group)
        #sprites
        self.import_player_assets()
        self.load_sprite('sprites/character/idle.png', (26, 26, 11, 13), 4, (255, 255, 255))
        self.rect = self.image.get_rect(center = pos)
        self.hitbox = self.rect.inflate(-15, -15)
        self.offset_y = 0
        self.x = pos[0]
        self.y = pos[1]
        self.status = 'down_idle'
        #movement
        self.direction = pygame.math.Vector2()
        self.velocity = 5
        #attack/magic
        self.can_attack = True
        self.attacking = False
        self.attack_cooldown = 700
        self.attack_time = None
        self.create_magic = create_magic 
        self.spell_list = ['ice', 'fire', 'wind', 'heal']
        self.spell_index = 0
        self.current_selected_spell = self.spell_list[self.spell_index]
        self.can_change_spell = True
        self.change_spell_cooldown = 300
        self.change_spell_time = None
        #taking damage
        self.is_vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 700
        #animation
        self.frame_index = 0
        self.animation_speed = 0.05
        #collision detection
        self.obstacle_sprites = obstacle_sprites
        #player stats
        self.stats = {'health': 100, 'mana': 100, 'magic': 10, 'speed': 5, 'defense': 5} #initial stats
        self.max_stats = {'health': 300, 'mana': 200, 'magic': 50, 'speed': 10, 'defense': 10} #ceiling of how much a stat can be increased by leveling up
        self.health = self.stats['health'] #current health
        self.mana = self.stats['mana'] #current mana
        self.mana_regen = self.stats['magic'] * 0.03
        self.exp = 0 #current exp
        self.exp_threshold = {'1': 30, '2':50, '3': 70, '4': 100, '5': 150, '6': 200, '7': 250, '8': 350} #exp needed to increase the lvl
        self.level = 1 #current level
        self.stats_points = 0 #stats points earned when leveling up
        #sounds
        self.player_levelup_sound = pygame.mixer.Sound('sounds/level_up.wav')
        self.player_walk_sound = pygame.mixer.Sound('sounds/step.wav')
        self.change_spell_sound = pygame.mixer.Sound('sounds/select_sound.wav')
        self.change_spell_sound.set_volume(0.3)
        self.walk_sound_cooldown = 12

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.attacking:
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up_run'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down_run'
            else:
                self.direction.y = 0
            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left_run'
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right_run'
            else:
                self.direction.x = 0

            if self.can_change_spell:
                if keys[pygame.K_LCTRL]:
                    self.can_change_spell = False
                    self.change_spell_time = pygame.time.get_ticks()
                    self.change_selected_spell()
                    self.change_spell_sound.play()

        if self.can_attack:
            if keys[pygame.K_SPACE]:
                if self.has_enough_mana(self.current_selected_spell):
                    self.direction = pygame.math.Vector2()
                    self.attacking = True
                    self.can_attack = False
                    self.attack_time = pygame.time.get_ticks()
                    self.create_magic(self.current_selected_spell)

    def change_selected_spell(self): #method that allows the player to cycle through all available spells
        self.spell_index += 1
        if self.spell_index >= len(self.spell_list):
            self.spell_index = 0
        self.current_selected_spell = self.spell_list[self.spell_index]

    def has_enough_mana(self, spell): #helper method that returns True if player has enough mana to cast the current active/selected spell
        return True if self.mana >= magic_data[spell]['cost'] else False

    def mana_regeneration(self): #method that handles passive mana regeneration
        self.mana += self.mana_regen
        if self.mana >= self.stats['mana']: #if current is the same as the maximum amount allowed based on the player's level/attributes
            self.mana = self.stats['mana']

    def get_player_total_damage(self): #total damage takes into consideration the spell's damage and the level of 'magic' status the player has
        if self.current_selected_spell != 'heal':
            total_damage = magic_data[self.current_selected_spell]['damage'] + self.stats['magic']
            return total_damage
        else:
            return 0

    def player_death(self):
        return True if self.health <= 0 else False

    def cooldowns(self): #method that handles ALL cooldowns -- attack/magic cooldown; changing spell cooldown; i-frames cooldown
        current_time = pygame.time.get_ticks()
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.can_attack = True
        
        if not self.can_change_spell:
            if current_time - self.change_spell_time >= self.change_spell_cooldown:
                self.can_change_spell = True

        if not self.is_vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.is_vulnerable = True

    def move(self, velocity): #method that handles player movement 
        if self.direction.magnitude() != 0: # if vector is something else than (0,0) -- normalize it to just get the direction of the vector
            self.direction = self.direction.normalize()

        #apply movement to the hitbox first and then apply to rect
        self.hitbox.x += self.direction.x * velocity
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * velocity
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def play_walking_sound(self):
        self.walk_sound_cooldown -= 1
        if self.walk_sound_cooldown <= 0:
            self.walk_sound_cooldown = 15    
            self.player_walk_sound.play()

    def collision(self, direction): #method that handles player collision with objects on the screen
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

    def get_status(self): #helper method to get current player status (attacking/moving/idle)
        if self.direction.x == 0 and self.direction.y == 0: #if the player is not moving at all
            if not 'idle' in self.status and not 'attack' in self.status: #if the player is not doing anything, it must be idle
                new_status = self.status.split('_') #status has the structure 'direction_status', therefore returns [direction, status]
                self.status = new_status[0] + '_idle'

        if self.attacking:
            #if player attacks, it stops its movement
            self.direction.x = 0
            self.direction.y = 0 
            if not 'attack' in self.status:
                status_parts = self.status.split('_') #split the status at the underline so that we can get the direction and just concatenate the 'attack' word
                self.status = status_parts[0] + '_attack'
        else: #if attack animation stops, player goes back to idle
            if 'attack' in self.status:
                self.status = self.status.replace('_attack','_idle')

    def increase_level(self): #helper method that increases player level if the experience threshold was overcome
        if self.exp >= self.exp_threshold[str(self.level)]:
            self.level += 1
            self.stats_points += 1
            self.exp = 0
            self.player_levelup_sound.play()

    def load_sprite(self, filename, frame, scale=None, color=None): #helper method to load an image (surface) by passing a sprite sheet and coordinates to extract a subsurface of the given spritesheet
        self.spritesheet = pygame.image.load(filename) #get the spritesheet
        self.image = self.spritesheet.subsurface(pygame.Rect(frame)) #extract a subsurface of the spritesheet by giving a coordinate (Rect) -> tuple (x, y, width, height)
        self.image = pygame.transform.scale(self.image, (frame[2] * scale, frame[3] * scale)) # get width and height from the frame (tuple) and scale them based on a given scale factor given
        self.image.set_colorkey(color) #removes background colour (colour is passed as argument) of the surface -- makes the png have a transparent background so it does not look weird on the game
        return self.image
 
    def import_player_assets(self): #populates the self.animation dictionary with all the sprites for each action (idle, run, attack)
        # get coordinates of the sprite in the spritesheet -- coordinates were extracted using GIMP on the specific spritesheet
        spritesheet_positions = {'up_idle': [(65,0,14,16), (65,26,13,16), (66,52,13,16)],'down_idle': [(44,0,14,16), (45,26,13,16), (44,52,13,16)],'left_idle': [(23,0,13,16), (23,26,12,16), (23,52,12,16)],'right_idle': [(1,0,13,16), (2,26,12,16), (2,52,12,16)],
			'right_run':[(2,2,12,14), (2,27,12,14), (2,68,12,14), (2,96,12,14), (2,122,12,14), (2,147,12,14), (2,188,13,14), (2,216,12,14)],'left_run':[(19,2,12,14), (18,27,13,14), (19,68,12,14), (19,96,12,14), (19,122,12,14), (19,147,12,14), (18,188,13,14), (19,216,12,14)],'down_run':[(35,1,13,15), (35,25,13,15),(34,49,14,15),(34,73,14,15),(35,94,13,15)],'up_run':[(54,1,13,15),(54,25,13,15,),(54,49,14,15),(54,73,14,15),(54,94,13,15)],
			'right_attack':[(3,3,12,14)],'left_attack':[(20,3,12,14)],'up_attack':[(55,2,13,15)],'down_attack':[(35,2,14,15)]}
        # create the dictionary that will be used by other methods
        self.animations = {'up_idle': [],'down_idle': [],'left_idle': [],'right_idle': [],
			'right_run':[],'left_run':[],'up_run':[],'down_run':[],
			'right_attack':[],'left_attack':[],'up_attack':[],'down_attack':[]}
        #populates the dictionary by passing the frame coordinate to the load_sprite method and appending it to the corresponding animation/direction
        for direction in spritesheet_positions:
            if spritesheet_positions[direction]: 
                for frame in spritesheet_positions[direction]:
                    if 'idle' in direction:
                        self.animations[direction].append(self.load_sprite('sprites/character/idle.png', frame, 4, (255, 255, 255)))
                    elif 'run' in direction:
                            self.animations[direction].append(self.load_sprite('sprites/character/run.png', frame, 4, (255, 255, 255)))
                    elif 'attack' in direction:
                        self.animations[direction].append(self.load_sprite('sprites/character/attack.png', frame, 4, (255, 255, 255)))

    def wave_value(self): #helper function to achieve "blinking" animation when taking damage
        value = sin(pygame.time.get_ticks())
        if value >= 0: 
            return 255
        else: 
            return 0

    def animate(self):
        #adapt animation speed based on the status of the player
        if 'run' in self.status:
            self.animation_speed = 0.17
            self.frame_index += self.animation_speed
        else:
            self.animation_speed = 0.1
            self.frame_index += self.animation_speed
        #loop over frames
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        #print the sprite on screen
        self.image = self.animations[self.status][int(self.frame_index)]
        self.rect = self.image.get_rect(topleft=self.hitbox.topleft) #movement is first applied to hitbox and then is applied back to the rect -- it's important to always update hitbox prior to rect because of collision

        if not self.is_vulnerable:
            alpha_value = self.wave_value()
            self.image.set_alpha(alpha_value)
        else:
            self.image.set_alpha(255)
            
    def update(self):
        self.input()
        self.get_status()
        self.cooldowns()
        self.animate()
        self.move(self.velocity)
        self.mana_regeneration()
        self.increase_level()
        self.player_death()
        # if 'run' in self.status:
        #     self.play_walking_sound()

        
