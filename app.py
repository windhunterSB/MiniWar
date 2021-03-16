import pygame
from pygame.locals import QUIT

from miniwar.game import Game
from miniwar.viewer import get_viewer

from ai.easycomputer.easycomputer import EasyComputer


def play_game(game, player_names, player_ais, seed, show=True):
    game.reset(seed)
    if show:
        viewer = get_viewer()
        viewer.update_timer(10)
        viewer.draw_and_tick(game.state, player_names)
    else:
        viewer = None
    while not game.state.is_game_over():
        if game.state.turn_i % 100 == 0:
            print("turn:", game.state.turn_i)
        game.before_turn()
        players_actions = []
        for pi in range(len(player_names)):
            state = game.get_numpy_state(pi)
            actions = player_ais[pi](state)
            players_actions.append(actions)

        for pi, actions in enumerate(players_actions):
            game.submit_strategy(pi, actions)

        game.after_turn()
        if show:
            viewer.draw_and_tick(game.state, player_names)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()


def run_app():
    player_names = [
        "yanzu", 
        "gouge", 
        "xqiang"]
    player_ais = [
        EasyComputer(0, 990), 
        EasyComputer(1, 999), 
        EasyComputer(2, 980)]
    game = Game(player_names)

    for seed in range(1000, 2000):
        play_game(game, player_names, player_ais, seed)


if __name__ == "__main__":
    run_app()
