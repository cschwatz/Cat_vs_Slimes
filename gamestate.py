import pygame

class GameState:
    def __init__(self):
        self.game_states = {'menu': True, 'new game': False, 'running': False, 'paused': False, 'lost': False, 'won': False, 'instructions': False}

    def change_game_state(self, state):
        for game_state in self.game_states.keys():
            if game_state == state:
                self.game_states[game_state] = True
            else:
                self.game_states[game_state] = False
    
    def get_current_state(self):
        for game_state in self.game_states.keys():
            if self.game_states[game_state]:
                return game_state
            