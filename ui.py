import pygame
pygame.font.init()

class UI:
    def __init__(self, player, monster_group):
        #initizalization
        self.import_UI_elements() #import UI elements sprites and icons
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('font/BitPotionExt.ttf', 48) #font and size
        self.font_stat_points = pygame.font.Font('font/BitPotionExt.ttf', 64)
        #get player object to help in some of the methods
        self.player = player
        #assign UI elements to variables, to make them easier to work with
        self.UI_bar = self.ui_elements['UI_bar']
        self.UI_spell_box = self.ui_elements['UI_spell_box']
        self.UI_stats_points_box = self.ui_elements['UI_stats_points_box']
        #monsters group -- assists in displaying the progress bar
        self.total_monsters = len(monster_group)

    def get_responsive_bar_width(self, bar_width, current_stat, max_stat): #method to work with responsive 'bars' -- HP/MP/Exp that increase/decrease based on specific events
        ratio = current_stat / max_stat #gets the proportion that the stat bar should be resized
        new_width = bar_width * ratio
        return new_width

    def display_hp(self):#helper function to display player's current hp
        player_max_hp = self.player.stats['health']
        player_current_hp = self.player.health
        player_hp_bar_container = self.UI_bar #UI bar image (surface)
        hp_text = self.font.render('HP', False, (0,0,0)) #text to go along the UI bar
        bar_width = self.get_responsive_bar_width(player_hp_bar_container.get_width(), player_current_hp, player_max_hp) #get UI bar width based on current hp
        #drawing onto the screen
        pygame.draw.rect(self.display_surface, (255,0,0), (10, 10, bar_width, player_hp_bar_container.get_height())) #draws the 'reponsive hp' onto the screen
        self.display_surface.blit(player_hp_bar_container, (10, 10, self.ui_elements['UI_bar'].get_width(), self.ui_elements['UI_bar'].get_height())) #draws the 'container' (UI) that the bar will be drawn on
        self.display_surface.blit(hp_text, (player_hp_bar_container.get_width() + 15, 3, hp_text.get_width(), hp_text.get_height()))

    def display_mp(self): #helper function to display the player's mana
        player_max_mp = self.player.stats['mana'] 
        player_current_mp = self.player.mana
        player_mp_bar_container = self.UI_bar #UI bar image (surface)
        mp_text = self.font.render('MP', False, (0,0,0)) #text to go along the UI bar
        bar_width = self.get_responsive_bar_width(player_mp_bar_container.get_width(), player_current_mp, player_max_mp) #get UI bar width based on current mana
        #drawing onto the screen
        pygame.draw.rect(self.display_surface, (0,0,255), (10, 45, bar_width, player_mp_bar_container.get_height())) #draws the 'reponsive hp' onto the screen
        self.display_surface.blit(player_mp_bar_container, (10, 45, self.ui_elements['UI_bar'].get_width(), self.ui_elements['UI_bar'].get_height())) #draws the 'container' (UI) that the bar will be drawn on
        self.display_surface.blit(mp_text, (player_mp_bar_container.get_width() + 15, 39, mp_text.get_width(), mp_text.get_height()))
    
    def display_exp(self): #helper function to display player's exp
        player_needed_exp = self.player.exp_threshold[str(self.player.level)]
        player_current_exp = self.player.exp
        player_exp_bar_container = self.UI_bar
        exp_text = self.font.render('EXP', False, (0,0,0)) #text to go along the UI bar
        bar_width = self.get_responsive_bar_width(player_exp_bar_container.get_width(), player_current_exp, player_needed_exp)
        #drawing onto the screen
        pygame.draw.rect(self.display_surface, (255,255,0), (650, 23, bar_width, player_exp_bar_container.get_height())) #draws the 'reponsive hp' onto the screen
        self.display_surface.blit(player_exp_bar_container, (650, 23, self.ui_elements['UI_bar'].get_width(), self.ui_elements['UI_bar'].get_height())) #draws the 'container' (UI) that the bar will be drawn on
        self.display_surface.blit(exp_text, (650 - exp_text.get_width(), 15, exp_text.get_width(), exp_text.get_height()))

    def display_spell_selection_box(self):
        spell_selection_box = self.UI_spell_box
        current_spell_text = self.font.render(f'{self.player.current_selected_spell}'.upper(), False, (0,0,0))
        current_spell = self.spell_icons[self.player.current_selected_spell]
        self.display_surface.blit(current_spell, (6, self.display_surface.get_height() - current_spell.get_height() + 5, current_spell.get_width(), current_spell.get_height()))
        self.display_surface.blit(spell_selection_box, (10, self.display_surface.get_height() - spell_selection_box.get_height(), spell_selection_box.get_width(), spell_selection_box.get_height()))
        self.display_surface.blit(current_spell_text, (30, self.display_surface.get_height() - spell_selection_box.get_height() - 40))

    def display_game_progress(self, current_num_monsters):
        total_number_of_monsters = self.total_monsters
        #objective is to kill at least 90% of the monsters
        player_current_progress = (total_number_of_monsters) - current_num_monsters #just subtracts the total number of monsters that are created when the level is instantiated and subtract it by the total amount of monster sprites -- if a monster is killed, its sprite is deleted, thus we can check how many are left
        progress_percentage = int((player_current_progress / total_number_of_monsters) * 100)
        progress_bar_container = self.UI_bar
        progress_bar_container_scaled = pygame.transform.scale(progress_bar_container, (progress_bar_container.get_width() * 1.5, progress_bar_container.get_height() * 1.5)) #scaling the bar beacause we need it to be bigger than other bars
        progress_bar_container_scaled.set_colorkey((255,255,255)) #remove white background that comes with the image
        progress_text = self.font.render(f'PROGRESS: {progress_percentage}%', False, (0,0,0))
        bar_width = self.get_responsive_bar_width(progress_bar_container_scaled.get_width(), player_current_progress, total_number_of_monsters)
        pygame.draw.rect(self.display_surface, (51,255,51), (300, 15, bar_width, progress_bar_container_scaled.get_height()))
        self.display_surface.blit(progress_bar_container_scaled, (300,15, self.ui_elements['UI_bar'].get_width(), self.ui_elements['UI_bar'].get_height()))
        self.display_surface.blit(progress_text, (330, 50, progress_text.get_width(), progress_text.get_height()))

    def display_available_stat_points(self):
        available_points = str(self.player.stats_points)
        available_points_text = self.font_stat_points.render(available_points, False, (255,0,0))
        stat_text = self.font.render('STAT', False, (0,0,0))
        points_text = self.font.render('POINTS', False, (0,0,0))
        self.display_surface.blit(self.UI_stats_points_box, (700, 60))
        self.display_surface.blit(available_points_text, (719, 57))
        self.display_surface.blit(stat_text, (700, 105))
        self.display_surface.blit(points_text, (690, 130))

    def import_UI_elements(self):
        #HP/MP/Exp bars and box that holds spell icons
        ui_elements_to_load = {'UI_bar': (6,5,96,20), 
                       'UI_spell_box': (260,180,88,88),
                       'UI_stats_points_box': (5,7,56,56)}
        self.ui_elements = {'UI_bar': None, 
                       'UI_spell_box': None,
                       'UI_stats_points_box': None}
        for element_type in ui_elements_to_load.keys(): #loading the ui elements into a dict
            if element_type == 'UI_bar':
                self.ui_elements[element_type] = self.load_sprite(f'sprites/UI/{element_type}.png', ui_elements_to_load[element_type], 1.5, (255,255,255))
            else:
                self.ui_elements[element_type] = self.load_sprite(f'sprites/UI/{element_type}.png', ui_elements_to_load[element_type], 0.95, (255,255,255))
        #spell icons that will be drawn at the 'current spell' box
        self.spell_icons = {'fire': None,
                        'wind': None,
                        'ice': None,
                        'heal': None}
        for spell_type in self.spell_icons.keys(): #loading spell icons into a dict
                spell_icon = pygame.image.load(f'sprites/UI/{spell_type}.png').convert_alpha()
                self.spell_icons[spell_type] = pygame.transform.scale(spell_icon, (spell_icon.get_width() * 5.8, spell_icon.get_height() * 5.8))

    def load_sprite(self, filename, frame, scale=None, color=None): #helper function to load an image (surface) by passing a sprite sheet and coordinates to extract a subsurface of the given spritesheet
        self.spritesheet = pygame.image.load(filename).convert_alpha() #get the spritesheet
        self.image = self.spritesheet.subsurface(pygame.Rect(frame)) #extract a subsurface of the spritesheet by giving a coordinate (Rect) -> tuple (x, y, width, height)
        self.image = pygame.transform.scale(self.image, (frame[2] * scale, frame[3] * scale)) # get width and height from the frame (tuple) and scale them based on a given scale factor given
        self.image.set_colorkey(color) #removes background colour (colour is passed as argument) of the surface -- makes the png have a transparent background so it does not look weird on the game
        return self.image

    def display(self, monsters_left):
        self.display_hp()
        self.display_mp()
        self.display_exp()
        self.display_game_progress(monsters_left)
        self.display_spell_selection_box()
        self.display_available_stat_points()