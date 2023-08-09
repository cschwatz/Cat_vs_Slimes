import pygame
pygame.font.init()

class Instructions:
    def __init__(self, game_state, main_menu):
        self.display_screen = pygame.display.get_surface()
        self.game_state = game_state
        self.image = pygame.image.load('backgrounds/fajrbackground.png')
        self.instructions_image = self.load_sprite('sprites/UI/Untitled.png', (7,3,615,454), 1.1, (255,255,255))
        self.button_background_image = self.load_sprite('sprites/UI/main_menu_button.png', (5,5,152,52),1,(255,255,255))
        self.font = self.font = pygame.font.Font('font/BitPotionExt.ttf', 64)
        #interaction
        self.can_interact = False
        self.can_interact_time = 100
        #main menu -- used to put a little timer before the player can interact with the menu
        self.main_menu = main_menu
        #sound
        self.return_sound = pygame.mixer.Sound('sounds/unpause.wav')

    def display_background(self):
        self.display_screen.blit(self.image, (0,0))

    def display_instructions(self):
        self.display_screen.blit(self.instructions_image, (60,20))
    
    def display_button(self):
        self.display_screen.blit(self.button_background_image, (320, 540))
        button_text = self.font.render('RETURN', False, (0,0,0))
        self.display_screen.blit(button_text, (340, 535))

    def input(self):
        keys = pygame.key.get_pressed()
        if self.can_interact:
            if keys[pygame.K_SPACE] or keys[pygame.K_ESCAPE]:
                self.main_menu.reset_interaction_timer()
                self.can_interact = False
                self.can_interact_time = 100
                self.game_state.change_game_state('menu')
                self.return_sound.play()

    def can_start_interacting(self): #this method's only purpose is to give a little delay for the player to be able to interact after the game has ended (makes it less wonky)
        if not self.can_interact:
            self.can_interact_time -= 5
            if self.can_interact_time <= 0:
                self.can_interact = True

    def load_sprite(self, filename, frame, scale=None, color=None): #helper method to load an image (surface) by passing a sprite sheet and coordinates to extract a subsurface of the given spritesheet
        image_surface = pygame.image.load(filename) #get the spritesheet
        image = image_surface.subsurface(pygame.Rect(frame)) #extract a subsurface of the spritesheet by giving a coordinate (Rect) -> tuple (x, y, width, height)
        image = pygame.transform.scale(image, (frame[2] * scale, frame[3] * scale)) # get width and height from the frame (tuple) and scale them based on a given scale factor given
        image.set_colorkey(color) #removes background colour (colour is passed as argument) of the surface -- makes the png have a transparent background so it does not look weird on the game
        return image

    def update(self):
        self.can_start_interacting()
        self.display_background()
        self.display_instructions()
        self.display_button()
        self.input()