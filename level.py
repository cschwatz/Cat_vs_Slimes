import pygame
from pytmx.util_pygame import load_pygame
from settings import *
from player import Player
from monster import Monster
from sprite import *
from random import choice
from magic import Projectile, Heal
from ui import UI
from levelup import LevelUp

class Level:
    def __init__(self, game_state):
        #screen
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_width() // 2
        self.half_height = self.display_surface.get_height() // 2
        #load tileset
        self.tmx_data = load_pygame('tileset/map/map.tmx')
        #sprite groups setup
        self.terrain_sprites = YSortCameraGroup() #group for the ground tiles (need to be drawn first)
        self.visible_sprites = YSortCameraGroup() #all sprites that are visible (group to draw them)
        self.obstacle_sprites = YSortCameraGroup() #spritre group for objects that have hitboxes
        self.magic_sprites = YSortCameraGroup() #sprite group for the spell's sprites
        self.attackable_sprites = pygame.sprite.Group() #group for monsters and bushes (sprites that can be attacked)
        self.monster_sprites = YSortCameraGroup() #group as a helper to deal with monster/player collision detection
        self.player_sprite = pygame.sprite.Group() #group that acts as a helper to deal with monster/player collision detecion
        self.quest_sprites = YSortCameraGroup() #helper group for the quest button that appears on the map
        self.text_sprites = YSortCameraGroup()
        #magic
        self.magic = None
        #monsters
        self.monster_list = []
        #create the level
        self.create_map()
        #UI -- goes after the level because it has to be drawn last (as it stays on top of other surfaces and needs the player object which is created in the create_map method)
        self.ui = UI(self.player, self.monster_list)
        self.levelup = LevelUp(self.player)
        #level_up_text
        self.level_up_duration = 60
        self.has_leveled_up = False
        self.font = pygame.font.Font('font/BitPotionExt.ttf', 64)
        #game states
        self.game_state = game_state
        self.can_pause = True
        self.pause_time = None
        self.pause_cooldown = 300
        #endgame
        self.has_achieved_objective = False
        #sounds
        self.pause_sound = pygame.mixer.Sound('sounds/pause.wav')
        self.unpause_sound = pygame.mixer.Sound('sounds/unpause.wav')

    def create_map(self): # function that creates all sprites that will be drawn on the level (screen)
        for layer in self.tmx_data.visible_layers:  
        #Barrier layer -- invisible, it's just for water/slope/houses hitbox
            if 'Barrier' in layer.name:
                for x,y,surf in layer.tiles():
                    pos = (x * 64, y * 64)
                    surf = pygame.transform.scale(surf, (surf.get_width() * 4, surf.get_height() * 4)) #convert width and height from 16 to 64
                    Barrier(pos, surf, self.obstacle_sprites, layer.name) 
        #Tile layers -- ground and houses
            if 'Terrain' in layer.name:
                for x,y,surf in layer.tiles(): #layer.tiles() returns a tuple (x, y, surf) of each Tile in the layer
                    #resize the tiles to be 64x64 (they are 16x16 originally) and multiply the positions by 64 so they align properly
                    pos = (x * 64, y * 64)
                    surf = pygame.transform.scale(surf, (surf.get_width() * 4, surf.get_height() * 4)) #convert width and height from 16 to 64
                    Generic(pos, surf, self.terrain_sprites) 
            if 'House' in layer.name:
                for x,y,surf in layer.tiles():
                    pos = (x * 64, y * 64)
                    surf = pygame.transform.scale(surf, (surf.get_width() * 4, surf.get_height() * 4))
                    Generic(pos, surf, self.terrain_sprites)
        #Object layers -- Trees, bushes and other objects
        for object in self.tmx_data.objects: #returns a list with all the objects from Tiled
            if object.name in ['Store', 'Tree', 'Object']: #these names are defined in Tiled -- object is a tuple with (x, y, surface) -- where the surface is the object's image
                surf = object.image
                surf = pygame.transform.scale(surf, (surf.get_width() * 4, surf.get_height() * 4)) # scale the object's image to convert it from 16x16 to 64x64
                Assets((object.x * 4, object.y * 4), surf, [self.visible_sprites, self.obstacle_sprites], object.name) # x and y position of the object is also multiplied by 4 to realign the object, since it has been scaled
            if object.name == 'Bush': #same process as other objects, but we want to assign it to a different sprite class, which will have different methods
                surf = object.image
                surf = pygame.transform.scale(surf, (surf.get_width() * 4, surf.get_height() * 4))
                Bush((object.x * 4, object.y * 4), surf, [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites], object.name) #assign to Bush class instead of Generic, because we have more methods
            if object.name == 'Spawn_point': #grab the marker object created in Tiled and get its coordinates (x,y) to know where to spawn the player
                player_spawn_point = (object.x * 4, object.y * 4)
                self.player = Player(player_spawn_point, [self.visible_sprites, self.player_sprite], self.obstacle_sprites, self.create_magic)
            if object.name == 'Monster_spawn':
                self.monster_list.append(Monster((object.x * 4, object.y * 4), choice(['blue', 'green', 'pink', 'purple']), [self.visible_sprites, self.attackable_sprites, self.monster_sprites], self.player, self.obstacle_sprites))
    
    def create_magic(self, spell_type): #helper function to pass the player object to the magic class so it can be used
        if spell_type in ['fire', 'ice', 'wind']:
            self.magic = Projectile(self.magic_sprites, self.player, self.player.status, self.player.rect, (self.player.hitbox.x, self.player.hitbox.y), spell_type, self.obstacle_sprites, self.attackable_sprites)
        else:
            self.magic = Heal(self.magic_sprites, self.player, spell_type, self.player.status)
        self.magic.mana_cost()

    def input(self):
        keys = pygame.key.get_pressed()
        if self.can_pause:
            if keys[pygame.K_RETURN] or keys[pygame.K_ESCAPE]:
                self.pause_time = pygame.time.get_ticks()
                self.can_pause = False
                if self.game_state.get_current_state() == 'running':
                    self.game_state.change_game_state('paused')
                    self.pause_sound.play()
                elif self.game_state.get_current_state() == 'paused':
                    self.game_state.change_game_state('running')
                    self.unpause_sound.play()

        if self.has_achieved_objective:
            if self.check_player_distance_from_objective():
                if keys[pygame.K_SPACE]:
                    self.game_state.change_game_state('won')

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.can_pause:
            if current_time - self.pause_time >= self.pause_cooldown:
                self.can_pause = True

    def attack_logic(self):
        if self.magic_sprites:
            for magic_sprite in self.magic_sprites:
                bush_sprite_collision = pygame.sprite.spritecollide(magic_sprite, self.attackable_sprites, False) #Bool is to kill the sprite -- collide sprites checks if magic_sprite collide with any sprite of the attackable_sprites group
                if bush_sprite_collision: #sprite_collision is a list -- sprite.spritecollide returns a list of the collisions
                    for bush_sprite in bush_sprite_collision:
                        if bush_sprite not in self.monster_sprites: #if the spell collided with a monster
                            if magic_sprite.spell != 'heal':
                                bush_sprite.kill()
                                magic_sprite.has_collided = True
                                magic_sprite.destroy_projectile()    
                monster_sprite_collision = pygame.sprite.spritecollide(magic_sprite, self.monster_sprites, False)
                if monster_sprite_collision:
                    for monster_sprite in monster_sprite_collision:
                        if magic_sprite.spell != 'heal':
                            monster_sprite.take_damage()
                            magic_sprite.has_collided = True
                            magic_sprite.destroy_projectile() 

    def check_win_condition(self): #win condition is met when player has killed 90% of the slimes on the map
        total_monsters_on_map = len(self.monster_list)
        current_monsters_on_map = len(self.monster_sprites)
        win_condition = total_monsters_on_map - (total_monsters_on_map * 0.9)
        if current_monsters_on_map < win_condition:
            self.has_achieved_objective = True

    def final_objective_coordinate(self): #gets the image and rect of the blessed statue (final objective of the game)
        statue = self.tmx_data.get_object_by_id(387) #id of the statue in Tiled
        statue_x = int(statue.x * 4)
        statue_y = int(statue.y * 4)
        if self.has_achieved_objective:
            quest_button_image = self.load_sprite('sprites/UI/final_quest_buttons.png', (4,4,56,56), 1, (255,255,255))
            quest_button_rect = quest_button_image.get_rect()
        else:
            quest_button_image = self.load_sprite('sprites/UI/final_quest_buttons.png', (64,4,56,56), 1, (255,255,255))
            quest_button_rect = quest_button_image.get_rect()
        quest_button_rect.x = statue_x + 14
        quest_button_rect.y = statue_y - 60
        return (quest_button_image, quest_button_rect)

    def check_player_distance_from_objective(self): #to handle if player has activated the main objective
        player_vector = pygame.math.Vector2(self.player.rect.center)
        statue = self.tmx_data.get_object_by_id(387)
        objective_rect = pygame.Rect(statue.x * 4, statue.y * 4, 50, 100)
        objective_vector = pygame.math.Vector2(objective_rect.center)
        distance = (player_vector - objective_vector).magnitude()
        return True if distance <= 75 else False

    def load_sprite(self, filename, frame, scale=None, color=None): #helper method to load an image (surface) by passing a sprite sheet and coordinates to extract a subsurface of the given spritesheet
        image_surface = pygame.image.load(filename) #get the spritesheet
        image = image_surface.subsurface(pygame.Rect(frame)) #extract a subsurface of the spritesheet by giving a coordinate (Rect) -> tuple (x, y, width, height)
        image = pygame.transform.scale(image, (frame[2] * scale, frame[3] * scale)) # get width and height from the frame (tuple) and scale them based on a given scale factor given
        image.set_colorkey(color) #removes background colour (colour is passed as argument) of the surface -- makes the png have a transparent background so it does not look weird on the game
        return image

    def player_take_damage_logic(self): #checks when player has collided with slime
        for monster_sprite in self.monster_sprites: 
            sprite_collision = pygame.sprite.spritecollide(monster_sprite, self.player_sprite, False)
            if sprite_collision:
                for index, sprite in enumerate(sprite_collision):
                    self.monster_list[index].damage_player()

    def check_player_level_up(self):
        if self.player.exp >= self.player.exp_threshold[str(self.player.level)]:
            self.has_leveled_up = True
    
    def level_up_text_animation(self): #animated text that indicates when player levels up
        level_up_text = self.font.render('LEVEL UP!', False, (0,0,0))
        level_up_text_rect = level_up_text.get_rect()
        level_up_text_rect.centerx = self.player.rect.centerx
        level_up_text_rect.centery = self.player.rect.centery - (100 - self.level_up_duration)
        self.level_up_duration -= 1
        if self.level_up_duration <= 0:
            self.has_leveled_up = False
            self.level_up_duration = 100
        return (level_up_text, level_up_text_rect)

    def run(self):
        self.input()
        self.cooldowns()
        self.terrain_sprites.custom_draw_ground(self.player) 
        self.visible_sprites.custom_draw(self.player) 
        self.magic_sprites.custom_draw_magic(self.player)
        self.monster_sprites.draw_monster_health_bars(self.player, self.monster_list)
        self.quest_sprites.draw_final_objective(self.player, self.game_state.get_current_state(), self.final_objective_coordinate())
        self.ui.display(len(self.monster_sprites))
        if self.has_leveled_up:
            self.text_sprites.draw_level_up_text(self.player, self.level_up_text_animation())
        if self.game_state.get_current_state() == 'running':
            self.terrain_sprites.update()
            self.visible_sprites.update()
            self.magic_sprites.update()
            self.attack_logic()
            self.player_take_damage_logic()
            self.check_win_condition()
            self.check_player_level_up()
            if self.player.player_death():
                self.game_state.change_game_state('lost')
        elif self.game_state.get_current_state() == 'paused':
            self.levelup.display_UI_background()
            self.levelup.display_UI()
            self.levelup.update()
            self.levelup.highlight_selected_item()
        
class YSortCameraGroup(pygame.sprite.Group): #Class that handles the camera -- It blits images on screen based on Y position. Thus, the surface that has the highest Y value should be blitted on top.
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface() #gets current active screen
        #camera offset
        self.offset = pygame.math.Vector2()
        self.half_screen_width = self.display_surface.get_width() // 2 
        self.half_screen_height = self.display_surface.get_height() // 2

    def center_target_camera(self, target): #passes player as parameter and checks its distance from top and left of the screen, because we want the player to be at the center of the screen at all times -- the result will be the amount we have to displace all visible sprites on the screen as the player moves
        self.offset.x = target.rect.centerx - self.half_screen_width
        self.offset.y = target.rect.centery - self.half_screen_height

    def get_responsive_bar_width(self, bar_width, current_stat, max_stat): #method to make monster hp bars responsive to damage 
        ratio = current_stat / max_stat 
        new_width = bar_width * ratio
        return new_width
    
    def draw_level_up_text(self, player, text): 
        self.center_target_camera(player)
        level_up_text = text[0]
        level_up_text_rect = text[1]
        offset_position = level_up_text_rect.topleft - self.offset
        self.display_surface.blit(level_up_text, offset_position)

    def draw_monster_health_bars(self, player, monster_list):
        self.center_target_camera(player)
        for index, _ in enumerate(monster_list):
            offset_position = monster_list[index].rect.topleft - self.offset
            hp_bar_width = self.get_responsive_bar_width(50, monster_list[index].health, monster_list[index].max_health)
            pygame.draw.rect(self.display_surface, (255,0,0), (offset_position[0] - 3, offset_position[1] - 15, hp_bar_width, 10))
    
    def draw_final_objective(self, player, game_state, objective):
        self.center_target_camera(player)
        offset_position = objective[1].topleft - self.offset
        self.display_surface.blit(objective[0], offset_position)

    def custom_draw(self, player):
        self.center_target_camera(player)
        for sprite in sorted(self.sprites(), key= lambda sprite:sprite.rect.centery): #accessing all sprites that have been stored in the sprite group and sorting them based on their Y value. Thus, blits first surfaces that have lower Y values and blits on top of them surfaces that have higher Y values.
            offset_position = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_position)

    def custom_draw_ground(self, player): #handles ground camera -- ground is not supposed to be blitted based on Y values, should always be below all other layers.
        self.center_target_camera(player)
        for sprite in self.sprites():
            offset_position = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_position)

    def custom_draw_magic(self, player): #handles ground camera -- ground is not supposed to be blitted based on Y values, should always be below all other layers.
        self.center_target_camera(player)
        for sprite in self.sprites():
            offset_position = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_position)
