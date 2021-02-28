import pygame
from pygame.locals import QUIT
import sys
import numpy as np


_viewer = None


class Viewer(object):
    def __init__(self):
        super(Viewer, self).__init__()
        pygame.init()
        pygame.display.set_caption('MiniWar')
        self.clock = pygame.time.Clock()
        self.screen_size = [800, 600]
        self.center = np.array([300, 300], dtype=np.float)
        self.scale = 4
        self.turn_offset = np.array([610, 10], dtype=np.float)
        self.population_rank_offset = np.array([610, 40], dtype=np.float)
        self.score_rank_offset = np.array([610, 240], dtype=np.float)
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
        self.city_title = np.array([-11, -16], dtype=np.float)
        self.troop_title = np.array([-8, -12], dtype=np.float)

    def update_timer(self, tick):
        self.tick_val = tick

    def draw_and_tick(self, state, player_names=None):
        self.screen.fill((244, 244, 244))
        fontcity = pygame.font.Font(pygame.font.get_default_font(), 10)
        fonttroop = pygame.font.Font(pygame.font.get_default_font(), 7)
        fontrank = pygame.font.Font(pygame.font.get_default_font(), 12)

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
            pos = (troop.traj[1] - troop.traj[0]) * (turn_i - troop.curr_turn) / \
                (troop.arrive_turn - troop.curr_turn) + troop.traj[0]
            pos = pos * self.scale + self.center
            pygame.draw.circle(self.screen, color, pos, 3)

            text = str(troop.level) + ":" + str(troop.size).rjust(3)
            text = fonttroop.render(text, True, color)
            self.screen.blit(text, pos + self.troop_title)

        self.turn_offset
        turn_text = "game progress:  {} / {}".format(state.turn_i, state.max_turn)
        text = fontrank.render(turn_text, True, (0, 0, 0))
        self.screen.blit(text, self.turn_offset)

        player_populations = [0] * state.player_num
        for city in state.cities:
            if city.owner == game_state.City.NO_OWNER_CITY:
                continue
            player_populations[city.owner] += city.population
        max_population = max(player_populations)
        max_population = max(max_population, 2000)
        populations = []
        for i, num in enumerate(player_populations):
            populations.append((i, num))
        populations = sorted(populations, key=lambda x: -x[1])
        
        population_title = "population rank:"
        text = fontrank.render(population_title, True, (0, 0, 0))
        self.screen.blit(text, self.population_rank_offset)

        row = 0
        for i, num in populations:
            row += 1
            color = self.player_color[i]
            text = str(i) if player_names is None else player_names[i]
            text = text.rjust(8) + ":"
            text_pos = self.population_rank_offset + np.array([0, row * 14])
            text = fontrank.render(text, True, color)
            self.screen.blit(text, text_pos)

            length = 120. * num / max_population
            rect = pygame.Rect(text_pos[0] + 40, text_pos[1], length + 1, 10)
            pygame.draw.rect(self.screen, color, rect)
        
        scores = []
        for i, sc in enumerate(state.player_scores):
            scores.append((i, sc))
        scores = sorted(scores, key=lambda x: -x[1])

        score_title = "score rank:"
        text = fontrank.render(score_title, True, (0, 0, 0))
        self.screen.blit(text, self.score_rank_offset)
        row = 0
        for i, sc in scores:
            row += 1
            color = self.player_color[i]
            text = str(i) if player_names is None else player_names[i]
            text = text.rjust(8) + ": " + "{:.2f}".format(sc).rjust(7)
            text_pos = self.score_rank_offset + np.array([0, row * 14])
            text = fontrank.render(text, True, color)
            self.screen.blit(text, text_pos)

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
    viwer.update_timer(10)

    state = game_state.GameState(3, seed=666, npc_num=40, max_turn=2000)

    for i in range(state.max_turn):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        players_actions = [[]] * 10
        for city in state.cities:
            if city.owner >= 0 and city.population >= 200:
                city_list = list(range(state.city_num))
                dists = []
                for to_city in city_list:
                    if state.cities[to_city].owner != city.owner:
                        dists.append((to_city, np.linalg.norm(
                            state.cities[to_city].pos2d - city.pos2d)))
                dists = sorted(dists, key=lambda x: x[1])
                for to_city, dist in dists:
                    if state.cities[to_city].owner != city.owner:
                        players_actions[city.owner].append((city.idx, to_city))

        for i in range(10):
            state.player_action(i, players_actions[i])

        state.update()
        viwer.draw_and_tick(state)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        viwer.clock.tick(viwer.tick_val)
