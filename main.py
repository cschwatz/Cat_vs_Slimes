import pygame
import sys
from settings import *
from level import Level
from gamestate import GameState
from mainmenu import MainMenu
from endscreen import EndScreen
from instructions import Instructions
pygame.mixer.init()
pygame.font.init()

class Game:
    def __init__(self):
          self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
          self.clock = pygame.time.Clock()
          self.game_state = GameState()
          self.main_menu = MainMenu(self.game_state)
          self.level = Level(self.game_state)
          self.end_screen = EndScreen(self.game_state)
          self.instructions = Instructions(self.game_state, self.main_menu)
          #sound
          self.bgm = pygame.mixer.Sound('sounds/music_bgm.mp3')
          self.bgm.set_volume(0.25)
          self.bgm.play(loops=-1)

    def run(self):
          while True:
               for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
               self.screen.fill((125, 125, 125))
               if self.game_state.get_current_state() == 'running' or self.game_state.get_current_state() == 'paused':
                    self.screen.fill(WATER_COLOR)
                    self.level.run()
               elif self.game_state.get_current_state() == 'new game':
                    self.screen.fill(WATER_COLOR)
                    self.level = Level(self.game_state)
                    self.game_state.change_game_state('running') 
               elif self.game_state.get_current_state() == 'menu':
                    self.main_menu.update()
               elif self.game_state.get_current_state() == 'won' or self.game_state.get_current_state() == 'lost':
                    self.end_screen.update()
                    if self.game_state.get_current_state == 'won':
                         self.end_screen.display_win_screen()
                    elif self.game_state.get_current_state == 'lost':
                         self.end_screen.display_lose_screen()
               elif self.game_state.get_current_state() == 'instructions':
                    self.instructions.update()

               pygame.display.update()
               self.clock.tick(FPS)
 
if __name__ == '__main__':
	game = Game()
	game.run()