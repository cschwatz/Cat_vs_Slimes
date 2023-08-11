import pygame
import sys
pygame.font.init()

class EndScreen:
    def __init__(self, game_state):
        self.display_screen = pygame.display.get_surface()
        self.background_image = pygame.image.load('backgrounds/nightbackgroundwithmoon.png')
        self.game_state = game_state
        self.options = ['new game', 'quit']
        self.button_list = []
        self.create_buttons()
        self.font = pygame.font.Font('font/BitPotionExt.ttf', 64)
        #banners
        self.win_banner_image = pygame.image.load('sprites/UI/congratulations_message.png')
        self.lose_banner_image = pygame.image.load('sprites/UI/failed_message.png')
        #interaction
        self.index = 0
        self.can_move_cursor = True
        self.cursor_moved_time = None
        self.move_cursor_cooldown = 300
        self.can_interact = False
        self.can_interact_time = 200
        #slime animation
        self.animation_frames = [(10, 5, 12, 11), (10,21,12,11), (11,34,10,11), (10,52,12,11),(10,69,12,11),(10,85,12,11), (9,101,14,11)]
        self.animations = []
        self.animation_index = 0
        self.animation_speed = 0.15
        self.import_slime_sprite()
        self.slime_image = self.animations[self.animation_index] 
        #sounds
        self.select_item_sound = pygame.mixer.Sound('sounds/select_sound.wav')
        self.move_cursor_sound = pygame.mixer.Sound('sounds/hover_item.wav')

    def display_background(self): #displays background image
        self.display_screen.blit(self.background_image, (0,0))

    def input(self): #deals with player input
        keys = pygame.key.get_pressed()
        if self.can_interact:
            if self.can_move_cursor:
                if keys[pygame.K_UP]:
                    self.cursor_moved_time = pygame.time.get_ticks()
                    self.can_move_cursor = False
                    self.move_cursor_sound.play()
                    self.index -= 1
                    if self.index < 0:
                        self.index = len(self.options) - 1

                elif keys[pygame.K_DOWN]:
                    self.cursor_moved_time = pygame.time.get_ticks()
                    self.can_move_cursor = False
                    self.index += 1
                    self.move_cursor_sound.play()
                    if self.index >= len(self.options):
                        self.index = 0
                
                if keys[pygame.K_SPACE] or keys[pygame.K_ESCAPE]:
                    current_selected_option = self.options[self.index]
                    self.button_list[self.index].trigger_button(current_selected_option)
                    self.select_item_sound.play()
    
    def can_start_interacting(self): #this method's only purpose is to give a little delay for the player to be able to interact after the game has ended (makes it less wonky)
        if not self.can_interact:
            self.can_interact_time -= 5
            if self.can_interact_time <= 0:
                self.can_interact = True

    def cooldown(self): #creates a delay between inputs
        current_time = pygame.time.get_ticks()
        if not self.can_move_cursor:
            if current_time - self.cursor_moved_time >= self.move_cursor_cooldown:
                self.can_move_cursor = True

    def create_buttons(self): #create button objects
        for _ in self.options:
            self.button_list.append(Button(self.game_state))

    def get_slime_y_position(self): #returns a y_position to blit slime onto the screen
        starting_y_pos = 350
        y_pos = starting_y_pos + (120 * self.index)        
        return y_pos
    
    def slime_animation(self):
        self.animation_index +=  self.animation_speed
        if self.animation_index >= len(self.animations):
            self.animation_index = 0
        self.slime_image = self.animations[int(self.animation_index)]
        slime_y_pos = self.get_slime_y_position()
        self.display_screen.blit(self.slime_image, (530, slime_y_pos))

    def load_sprite(self, filename, frame, scale=None, color=None): #helper method to load an image (surface) by passing a sprite sheet and coordinates to extract a subsurface of the given spritesheet
        image_surface = pygame.image.load(filename) #get the spritesheet
        image = image_surface.subsurface(pygame.Rect(frame)) #extract a subsurface of the spritesheet by giving a coordinate (Rect) -> tuple (x, y, width, height)
        image = pygame.transform.scale(image, (frame[2] * scale, frame[3] * scale)) # get width and height from the frame (tuple) and scale them based on a given scale factor given
        image.set_colorkey(color) #removes background colour (colour is passed as argument) of the surface -- makes the png have a transparent background so it does not look weird on the game
        return image
    
    def import_slime_sprite(self):
        for frame in self.animation_frames:
            self.animations.append(self.load_sprite('sprites/monsters/green_front.png', frame, 6, (255,255,255)))

    def display_buttons(self): #display the button objects
        button_x_pos = 280
        button_y_pos = 350
        for index, button in enumerate(self.button_list):
            #button
            button.display_button(button_x_pos, button_y_pos)
            #text
            button.display_text(self.options[index].upper())
            button_y_pos += 120

    def display_win_screen(self): #if player has won
        self.display_screen.blit(self.win_banner_image, (115, 170))
        final_text = self.font.render('THANKS FOR PLAYING. THIS WAS CS50!', False, (0,0,0))
        self.display_screen.blit(final_text, (100, 270))

    def display_lose_screen(self): #if player lost
        self.display_screen.blit(self.lose_banner_image, (200,170))

    def update(self):
        self.display_background()
        self.display_buttons()
        if self.game_state.get_current_state() == 'won':
            self.display_win_screen()
        elif self.game_state.get_current_state() == 'lost':
            self.display_lose_screen()
        self.can_start_interacting()
        self.input()
        self.cooldown()
        self.slime_animation()
        

class Button:
    def __init__(self, game_state):
        self.display_screen = pygame.display.get_surface()
        self.button_background_image = self.load_sprite('sprites/UI/main_menu_button.png', (5,5,152,52),1.5,(255,255,255))
        self.rect = self.button_background_image.get_rect()
        self.font = self.font = pygame.font.Font('font/BitPotionExt.ttf', 64)
        self.game_state = game_state
    
    def display_button(self, x, y): #blit the button image
        self.rect.x = x
        self.rect.y = y
        self.display_screen.blit(self.button_background_image, (x, y))

    def display_text(self, text): #blit button text
        start_text = self.font.render(text, False, (0,0,0))
        text_rect = start_text.get_rect()
        text_rect.centerx = self.rect.centerx
        text_rect.centery = self.rect.centery - 3
        self.display_screen.blit(start_text, (text_rect.x, text_rect.y))

    def trigger_button(self, state): #if button has been "clicked"
        if state == 'new game':
            self.game_state.change_game_state('new game')
        else:
            pygame.quit()
            sys.exit()

    def load_sprite(self, filename, frame, scale=None, color=None): #helper method to load an image (surface) by passing a sprite sheet and coordinates to extract a subsurface of the given spritesheet
        image_surface = pygame.image.load(filename) #get the spritesheet
        image = image_surface.subsurface(pygame.Rect(frame)) #extract a subsurface of the spritesheet by giving a coordinate (Rect) -> tuple (x, y, width, height)
        image = pygame.transform.scale(image, (frame[2] * scale, frame[3] * scale)) # get width and height from the frame (tuple) and scale them based on a given scale factor given
        image.set_colorkey(color) #removes background colour (colour is passed as argument) of the surface -- makes the png have a transparent background so it does not look weird on the game
        return image
    

