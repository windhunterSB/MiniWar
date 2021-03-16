import numpy as np


class EasyComputer(object):
    def __init__(self, player_id, max_population=200):
        super().__init__()
        self.player_id = player_id
        self.max_population = max_population

    def __call__(self, state):
        state = state["city"]
        ret = []
        for ci in range(state.city_num()):
            if state.owner(ci) != self.player_id:
                continue
            if state.population(ci) < self.max_population:
                continue
            pos2d = state.pos2d(ci)
            dists = []
            for to_city in range(state.city_num()):
                if state.owner(to_city) != self.player_id:
                    dists.append((to_city, np.linalg.norm(
                        state.pos2d(to_city) - pos2d)))
            if dists:
                dists = sorted(dists, key=lambda x: x[1])
                ret.append((ci, dists[0]))
        return ret
