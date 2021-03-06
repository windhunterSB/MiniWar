import time

from .game_state import GameState
from .viewer import get_viewer


class Game(object):
    def __init__(self, player_names, open_viewer=True):
        super().__init__()
        self.viewer = get_viewer() if open_viewer else None
        if self.viewer:
            self.viewer.update_timer(10)
        self.state = None
        self.player_num = len(player_names)
        self.player_names = player_names
        self.player_id = {}
        for i, name in enumerate(player_names):
            self.player_id[name] = i

    def _draw_and_tick(self):
        if self.viewer:
            self.viewer.draw_and_tick(self.state, self.player_names)

    def reset(self, seed, npc_num=20):
        if seed == -1:
            seed = int(time.time())
        self.state = GameState(self.player_num, seed, npc_num, max_turn=1600)
        self._draw_and_tick()
    
    def get_curr_state(self):
        pass

    def submit_strategy(self, player_name, operations):
        pass
          
