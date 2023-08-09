import pygame
from magic import Magic

class Projectile(Magic):
    def __init__(self, groups, direction, spell, image_dict, pos, player_pos, player_rect, obstacle_group, attackable_group):
        super().__init__()
        #player
        self.player_pos = player_pos
        self.player_rect = player_rect
        self.player_direction = direction.split('_')[0] #passed in as argument from the player class -- gets the player status which has the following format str: 'direction_status'
        #spell animation
        self.spell = spell
        self.magic_animations = image_dict
        self.frame_index = 0
        self.animation_speed = 0.25
        self.image = self.magic_animations['start'][self.frame_index]
        self.get_player_facing_position(self.player_direction) #gets image.rect based on the direction the player is facing and also transforms (rotate/flip) the spell sprite based on the direction the player is facing
        self.hitbox = self.rect
        self.was_cast = True
        self.is_active = False
        self.has_collided = False
        # self.play_start_animation()
        #movement
        self.projectile_direction = pygame.math.Vector2()
        self.projectile_velocity = 5
        self.maximum_distance = 300 #maximum distance that the projectile can travell before disappearing
        #collision
        self.attackable_group = attackable_group
        self.obstacle_group = obstacle_group
        
    
    def get_player_facing_position(self, direction): #gets player position/direction to know where to spawn the spell (when spell is cast)
        if direction == 'right':
            self.rect = self.image.get_rect(midleft=self.player_rect.midright + pygame.math.Vector2(0,2))
        elif direction == 'left':
            for animation_type in self.magic_animations.keys():
                for frame in self.magic_animations[animation_type]:
                    frame = pygame.transform.flip(self.image, True, False)
                    frame.set_colorkey((255,255,255))
            self.image = self.magic_animations['start'][self.frame_index]
            self.rect =  self.image.get_rect(midright=self.player_rect.midleft + pygame.math.Vector2(0,2))
        elif direction == 'up':
            self.image = pygame.transform.rotate(self.image, 90)
            self.image.set_colorkey((255,255,255))
            self.rect =  self.image.get_rect(midbottom=self.player_rect.midtop)
        else:
            self.image = pygame.transform.rotate(self.image, 270)
            self.image.set_colorkey((255,255,255))
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
        if int(self.travelled_distance()) > self.maximum_distance:
            self.play_projectile_end_animation()

    def check_projectile_collision(self):
        for sprite in self.obstacle_group:
            if sprite.hitbox.colliderect(self.hitbox):
                self.has_collided = True
                self.play_projectile_end_animation()
        for sprite in self.attackable_group:
            if sprite.hitbox.colliderect(self.hitbox):
                self.has_collided = True
                self.play_projectile_end_animation()

    def play_projectile_start_animation(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.magic_animations['start']):
            self.frame_index = 0
        
    def play_projectile_end_animation(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.magic_animations['hit']):
                self.frame_index = 0
                self.kill()
        self.image = self.magic_animations['hit'][int(self.frame_index)]
        self.rect = self.image.get_rect(topleft=self.hitbox.topleft)

    def animate(self):
        if not int(self.travelled_distance()) > self.maximum_distance and not self.has_collided:
            #self.frame_index += self.animation_speed
            if self.was_cast:
                self.frame_index += 0.15
                if self.frame_index >= len(self.magic_animations['start']):
                    self.frame_index = 0
                    self.was_cast = False
                    self.is_active = True
                self.image = self.magic_animations['start'][int(self.frame_index)]
                self.rect = self.image.get_rect(topleft=self.hitbox.topleft)
            
            if self.is_active:
            #loop over frames
                self.frame_index += self.animation_speed
                if self.frame_index >= len(self.magic_animations['moving']):
                    self.frame_index = 0
                self.image = self.magic_animations['moving'][int(self.frame_index)]
                self.rect = self.image.get_rect(topleft=self.hitbox.topleft)

    def update(self):
        self.move_projectile()
        self.check_projectile_collision()
        self.destroy_projectile()
        self.animate()
