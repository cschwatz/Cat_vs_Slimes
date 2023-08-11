import pygame

class LevelUp:
    def __init__(self, player):
        self.display_surface = pygame.display.get_surface()
        self.font = self.font = pygame.font.Font('font/BitPotionExt.ttf', 64)
        self.player = player
        self.number_of_attributes = len(self.player.stats)
        self.item_list = []
        self.index = 0 
        self.can_move_cursor = True
        self.cursor_movement_cooldown = 200
        self.moved_cursor_time = None
        self.window_image = self.load_sprite('sprites/UI/level_up_window2.png', (27,21,353,261), 2, (255,255,255))
        self.button_image = self.load_sprite('sprites/UI/button.png', (6,4,56,56), 1, (255,255,255))
        self.create_items()
        #sounds
        self.move_cursor_sound = pygame.mixer.Sound('sounds/hover_item.wav')
        self.move_cursor_sound.set_volume(0.7)

    def input(self):
        keys = pygame.key.get_pressed()
        if self.can_move_cursor:
            if keys[pygame.K_UP]:
                self.can_move_cursor = False
                self.moved_cursor_time = pygame.time.get_ticks()
                self.move_cursor_sound.play()
                self.index -= 1
                if self.index < 0:
                    self.index = len(self.item_list) - 1
            elif keys[pygame.K_DOWN]:
                self.can_move_cursor = False
                self.moved_cursor_time = pygame.time.get_ticks()
                self.move_cursor_sound.play()
                self.index += 1
                if self.index >= len(self.item_list):
                    self.index = 0
            if keys[pygame.K_SPACE]:
                self.can_move_cursor = False
                self.moved_cursor_time = pygame.time.get_ticks()
                self.item_list[self.index].trigger_button(self.index)

    def cooldown(self):
        current_time = pygame.time.get_ticks()
        if not self.can_move_cursor:
            if current_time - self.moved_cursor_time >= self.cursor_movement_cooldown:
                self.can_move_cursor = True

    def highlight_selected_item(self):
        current_item = self.item_list[self.index]
        for item in self.item_list:
            if item == current_item:
                pygame.draw.rect(self.display_surface, (255,255,0), (item.rect.x, item.rect.y, item.image.get_width(), item.image.get_height()), 3)
    
    def create_items(self):
        for _ in range(self.number_of_attributes):
            self.item_list.append(Item(self.player))

    def display_UI_background(self):
        self.display_surface.blit(self.window_image, (50, 50))

    def display_UI(self):
        text_x_pos = 100
        text_y_pos = 70
        button_y_pos = 70
        stats_points_message = self.font.render(f'Stats points remaining: {self.player.stats_points}', False, (0,0,0))
        self.display_surface.blit(stats_points_message, (160, 80))

        for index, item in enumerate(self.item_list):
            #text
            text_y_pos += 80
            attribute_text = list(self.player.stats.keys())[index]
            attribute_text_to_display =  attribute_text.title() + f': {self.player.stats[attribute_text]}'
            item.display_text(text_x_pos, text_y_pos, attribute_text_to_display)
            
            #button
            button_x_pos = item.text_display.get_width() + 120
            button_y_pos += 80
            item.display_button(button_x_pos, button_y_pos)

            #text2
            max_attribute_text = list(self.player.max_stats.keys())[index]
            max_attribute_text_to_display = f'Max {max_attribute_text}: {self.player.max_stats[max_attribute_text]}'
            item.display_text(text_x_pos + 300, text_y_pos, max_attribute_text_to_display)

    def load_sprite(self, filename, frame, scale=None, color=None): #helper method to load an image (surface) by passing a sprite sheet and coordinates to extract a subsurface of the given spritesheet
        image_surface = pygame.image.load(filename) #get the spritesheet
        image = image_surface.subsurface(pygame.Rect(frame)) #extract a subsurface of the spritesheet by giving a coordinate (Rect) -> tuple (x, y, width, height)
        image = pygame.transform.scale(image, (frame[2] * scale, frame[3] * scale)) # get width and height from the frame (tuple) and scale them based on a given scale factor given
        image.set_colorkey(color) #removes background colour (colour is passed as argument) of the surface -- makes the png have a transparent background so it does not look weird on the game
        return image
    
    def update(self):
        self.input()
        self.cooldown()
        for index, item in enumerate(self.item_list):
            item.update_button_image(index)

class Item:
    def __init__(self, player):
        self.display_surface = pygame.display.get_surface()
        self.available_button_image = self.load_sprite('sprites/UI/button_available.png', (6,4,56,56), 1, (255,255,255))
        self.unavailable_button_image = self.load_sprite('sprites/UI/button_unavailable.png', (6,4,56,56), 1, (255,255,255))
        self.image = self.available_button_image
        self.rect = self.image.get_rect()
        self.font = self.font = pygame.font.Font('font/BitPotionExt.ttf', 64)
        self.player = player
        self.can_upgrade = True
        #sounds
        self.level_up_stat_sound = pygame.mixer.Sound('sounds/level_up_stat.wav')
        self.level_up_stat_sound.set_volume(0.5)

    def display_text(self, x, y, text):
        self.text_display = self.font.render(text, False, (0,0,0))
        self.display_surface.blit(self.text_display, (x, y))

    def display_button(self, x, y):
        self.display_surface.blit(self.image, (x, y))
        self.rect.x = x
        self.rect.y = y

    def check_if_stat_is_maxed(self, index):
        attribute_to_upgrade = list(self.player.stats.keys())[index]
        #if stat is maxed out
        if self.player.stats[attribute_to_upgrade] >= self.player.max_stats[attribute_to_upgrade]:
            self.can_upgrade = False
        
    def update_button_image(self, index):
        self.check_if_stat_is_maxed(index)
        if self.can_upgrade and self.player.stats_points > 0:
            self.image = self.available_button_image
        else:
            self.image = self.unavailable_button_image

    def load_sprite(self, filename, frame, scale=None, color=None): #helper method to load an image (surface) by passing a sprite sheet and coordinates to extract a subsurface of the given spritesheet
        image_surface = pygame.image.load(filename) #get the spritesheet
        image = image_surface.subsurface(pygame.Rect(frame)) #extract a subsurface of the spritesheet by giving a coordinate (Rect) -> tuple (x, y, width, height)
        image = pygame.transform.scale(image, (frame[2] * scale, frame[3] * scale)) # get width and height from the frame (tuple) and scale them based on a given scale factor given
        image.set_colorkey(color) #removes background colour (colour is passed as argument) of the surface -- makes the png have a transparent background so it does not look weird on the game
        return image

    def trigger_button(self, index):
        attribute_to_upgrade = list(self.player.stats.keys())[index] #get the stat we're working with based on the index
        #if the player has an upgrade point to spend and the attribute to upgrade has not yet reached its maximum
        if self.can_upgrade:
            if self.player.stats_points > 0:
                if attribute_to_upgrade == 'health':
                    self.player.stats_points -= 1
                    self.player.stats[attribute_to_upgrade] += 50
                elif attribute_to_upgrade == 'mana':
                    self.player.stats_points -= 1
                    self.player.stats[attribute_to_upgrade] += 20
                elif attribute_to_upgrade == 'magic':
                    self.player.stats_points -= 1
                    self.player.stats[attribute_to_upgrade] += 10
                else:
                    self.player.stats_points -= 1
                    self.player.stats[attribute_to_upgrade] += 1
                self.level_up_stat_sound.play()
                