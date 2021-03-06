import numpy as np
import random
import math


class Troop(object):
    def __init__(self,
                 owner, from_city, to_city,
                 size, curr_turn, arrive_turn, traj, lev):
        super().__init__()
        self.owner = owner
        self.from_city = from_city
        self.to_city = to_city
        self.size = size
        self.curr_turn = curr_turn
        self.arrive_turn = arrive_turn
        self.traj = traj  # [(sx, sy), (ex, ey)]
        self.level = lev


class City(object):
    NO_OWNER_CITY = -1
    NEXT_LEVEL_EXP = {
      0: 5000,
      1: 10000,
      2: 20000,
      3: 40000,
      4: 80000,
    }

    def __init__(self, idx, owner, pos2d, init_growth):
        super().__init__()
        self.idx = idx
        self.owner = owner
        self.pos2d = pos2d
        self.growth = init_growth
        self.population = 0 if owner != City.NO_OWNER_CITY else 1000
        self.level = 0
        self.exp = 0

    def exp_update(self):
        if self.level not in City.NEXT_LEVEL_EXP:
            return
        self.exp += int(self.population / 2)
        if self.exp >= City.NEXT_LEVEL_EXP[self.level]:
            self.exp -= City.NEXT_LEVEL_EXP[self.level]
            self.level += 1

    def population_update(self):
        if self.owner == City.NO_OWNER_CITY:
            return
        self.population += self.growth + int(self.population * 0.02)
        self.population = min(self.population, 1000)

    def battle(self, troop):
        if troop.owner == self.owner:
            self.population += int(troop.size * 0.5)
        else:
            self.population -= int(troop.size * (1. + 0.1 * troop.level) / (1. + 0.2 * self.level))
            if self.population < 0:
                # loss
                self.population = -self.population
                self.owner = troop.owner
                self.level = int(self.level / 2)
                self.exp = 0
            else:
                # win: recover some population
                self.population += int(troop.size * 0.2)
        self.population = min(self.population, 1000)

    def gene_troop(self, to_city, curr_turn):
        if self.idx == to_city.idx:
            return None
        if to_city.owner == self.owner:
            return None
        size = int(self.population / 2)
        if size < 10:
            return None
        dist = np.linalg.norm(self.pos2d - to_city.pos2d) / 1.5
        arrive_turn = curr_turn + int(dist + 0.5) + 1
        self.population -= size
        traj = (self.pos2d, to_city.pos2d)
        return Troop(
            self.owner, self.idx, to_city.idx,
            size, curr_turn, arrive_turn, traj, self.level)


class GameState(object):
    def __init__(self, player_num, seed, npc_num=20, max_turn=1000):
        super().__init__()
        self.seed = seed
        self.city_num = npc_num + player_num
        self.max_turn = max_turn
        self.turn_i = 0
        self.cities = []
        self.troops = []
        self.player_num = player_num
        self.player_scores = [0] * player_num
        self.reset()

    def reset(self):
        random.seed(self.seed)
        self.turn_i = 0
        self.cities = []
        self.troops = []
        self.player_scores = [0] * self.player_num

        radius = 60.

        player_init_growth = random.randrange(3, 10)
        for i in range(self.player_num):
            yaw = math.pi * 2.0 * i / self.player_num
            pos = np.array([math.cos(yaw) * radius, math.sin(yaw) * radius])
            self.cities.append(City(i, i, pos, player_init_growth))

        for j in range(self.player_num, self.city_num):
            pos = np.array([
                (random.random() - 0.5) * radius * 2,
                (random.random() - 0.5) * radius * 2], dtype=np.float)
            self.cities.append(
                City(j, City.NO_OWNER_CITY, pos, random.randrange(3, 10)))

    def update(self):
        if self.turn_i >= self.max_turn:
            # game over
            return False

        self.troops = sorted(self.troops, key=lambda x: x.arrive_turn)
        self.turn_i += 1

        # level update first
        for city in self.cities:
            city.exp_update()

        # fight second
        arrive_i = -1
        for i in range(len(self.troops)):
            troop = self.troops[i]
            if troop.arrive_turn == self.turn_i:
                arrive_i = i
                city = self.cities[troop.to_city]
                city.battle(troop)
        if arrive_i >= 0:
            self.troops = self.troops[arrive_i + 1:]

        # growth third
        for city in self.cities:
            city.population_update()

        # update scores
        total_num = 0
        for city in self.cities:
            if city.owner == City.NO_OWNER_CITY:
                continue
            total_num += city.population
        for city in self.cities:
            if city.owner == City.NO_OWNER_CITY:
                continue
            self.player_scores[city.owner] += 1. * city.population / total_num
        
    def player_action(self, player_i, actions):
        action_loss = 0
        from_cities_set = set()
        for action in actions:
            from_city, to_city = action
            if from_city in from_cities_set:
                action_loss -= 10
                continue
            if from_city < 0 or from_city >= self.city_num or to_city < 0 or to_city >= self.city_num:
                action_loss -= 10
                continue
            city = self.cities[from_city]
            if city.owner != player_i:
                action_loss -= 10
                continue
            troop = city.gene_troop(self.cities[to_city], self.turn_i)
            if troop is None:
                action_loss -= 10
                continue
            self.troops.append(troop)
            from_cities_set.add(from_city)

        return action_loss

    def get_numpy_state(self):
        pass
