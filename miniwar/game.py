import time
import numpy as np

from .game_state import GameState
from .viewer import get_viewer


class CityStateNp(object):
    def __init__(self, np):
        super().__init__()
        self.state_np = np

    def get_state_col_names(self):
        return ["owner", "x", "y", "growth", "population", "level"]

    def np_data(self):
        return self.state_np

    def owner(self, city_i):
        return self.state_np[city_i][0]

    def pos2d(self, city_i):
        return self.state_np[city_i][1:3]

    def growth(self, city_i):
        return self.state_np[city_i][3]

    def population(self, city_i):
        return self.state_np[city_i][4]

    def level(self, city_i):
        return self.state_np[city_i][5]

    def city_num(self):
        return len(self.state_np)


class TroopStateNp(object):
    def __init__(self, np):
        super().__init__()
        self.state_np = np

    def get_state_col_names(self):
        return ["owner", "x", "y", "size", "level"]

    def owner(self, troop_i):
        return self.state_np[troop_i][0]

    def pos2d(self, troop_i):
        return self.state_np[troop_i][1:3]

    def size(self, troop_i):
        return self.state_np[troop_i][3]

    def level(self, troop_i):
        return self.state_np[troop_i][4]

    def troop_num(self):
        return len(self.state_np)


class Game(object):
    def __init__(self, player_names):
        super().__init__()
        self.state = None
        self.player_num = len(player_names)
        self.player_names = player_names
        self.player_id = {}
        for i, name in enumerate(player_names):
            self.player_id[name] = i
        self.state_records = {}
        self.score_records = {}

    def reset(self, seed, npc_num=20):
        if seed == -1:
            seed = int(time.time())
        self.state_records = {}
        self.score_records = {}
        self.state = GameState(self.player_num, seed, npc_num, max_turn=1000)

    def get_player_id(self, name):
        return self.player_id[name]

    def before_turn(self):
        assert(self.state.turn_i not in self.state_records)
        np_state = self.state.get_numpy_state()
        self.state_records[self.state.turn_i] = np_state
        self.score_records[self.state.turn_i] = np.array(
            self.state.player_scores, dtype=np.float32)

    def after_turn(self):
        self.state.update()

    def get_numpy_state(self, player_id):
        assert(self.state.turn_i in self.state_records)
        np_state = self.state_records[self.state.turn_i]
        return {
            "city": CityStateNp(np.copy(np_state["city"])),
            "troop": TroopStateNp(np.copy(np_state["troop"])),
        }

    def submit_strategy(self, player_id, actions):
        # action: [from_city, to_city]
        # actions: [action0, action1, ...]
        loss = self.state.player_action(player_id, actions)
        return loss
