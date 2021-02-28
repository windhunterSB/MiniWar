import pygame
from pygame.locals import QUIT
import sys
import numpy as np


_viewer = None


class Viewer(object):
    def __init__(self):
        super(Viewer, self).__init__()
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen_size = [800, 600]
        self.center = np.array([300, 300], dtype=np.float)
        self.scale = 4
        self.screen = pygame.display.set_mode(self.screen_size)
        self.screen.fill((233, 233, 233))
        pygame.display.flip()
        self.tick_val = 10

        self.player_color = {
          -1: (137, 137, 137),
          0: (253, 21, 50),
          1: (31, 26, 249),
          2: (39, 235, 69),
          3: (255, 128, 0),
          4: (207, 48, 203),
          5: (114, 125, 203),
          6: (10, 10, 10),
          7: (10, 128, 96),
          8: (120, 120, 10),
          9: (90, 111, 240),
        }

        self.city_points = np.array(
            [[-4, -6], [4, -6], [4, -3],
             [10, 6], [-10, 6], [-4, -3]], np.float)
        self.city_title = np.array([-10, -16], dtype=np.float)
        self.troop_title = np.array([-8, -12], dtype=np.float)

    def update_timer(self, tick):
        self.tick_val = tick
    
    def draw_and_tick(self, state):
        self.screen.fill((244, 244, 244))
        fontcity = pygame.font.Font(pygame.font.get_default_font(), 10)
        fonttroop = pygame.font.Font(pygame.font.get_default_font(), 7)

        for city in state.cities:
            color = self.player_color[city.owner]
            pos = city.pos2d * self.scale + self.center
            points = self.city_points + pos
            pygame.draw.polygon(self.screen, color, points)
            
            text = str(city.level) + ":" + str(city.population).rjust(4)
            text = fontcity.render(text, True, color)
            self.screen.blit(text, pos + self.city_title)

        turn_i = state.turn_i
        for troop in state.troops:
            color = self.player_color[troop.owner]
            pos = (troop.traj[1] - troop.traj[0]) * (turn_i - troop.curr_turn) / (troop.arrive_turn - troop.curr_turn) + troop.traj[0]
            pos = pos * self.scale + self.center
            pygame.draw.circle(self.screen, color, pos, 3)

            text = str(troop.level) + ":" +str(troop.size).rjust(3)
            text = fonttroop.render(text, True, color)
            self.screen.blit(text, pos + self.troop_title)

        pygame.display.flip()
        self.clock.tick(self.tick_val)


def get_viewer():
    global _viewer
    if not _viewer:
        _viewer = Viewer()
    return _viewer


if __name__ == "__main__":
    import game_state
    viwer = get_viewer()

    state = game_state.GameState(4, seed=111, npc_num=20)

    for i in range(1000):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        viwer.draw_and_tick(state)
        state.update()

        players_actions = [[]] * 10
        for city in state.cities:
            if city.owner >= 0 and city.population >= 200:
                city_list = list(range(state.city_num))
                dists = []
                for to_city in city_list:
                    if state.cities[to_city].owner != city.owner:
                        dists.append((to_city, np.linalg.norm(state.cities[to_city].pos2d - city.pos2d)))
                dists = sorted(dists, key=lambda x: x[1])
                for to_city, dist in dists:
                    if state.cities[to_city].owner != city.owner:
                        players_actions[city.owner].append((city.idx, to_city))
        
        for i in range(10):
            state.player_action(i, players_actions[i])

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        viwer.clock.tick(viwer.tick_val)


