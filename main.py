import time

import pygame

from game.SnakeGame import SnakeGame, Direction


def main():
    pygame.init()

    rows = 10
    columns = 10
    input_size = rows * columns

    actions = Direction

    env = SnakeGame(600, 600, rows, columns, 10)

    episodes = 10
    for i in range(episodes):
        env.reset()

        state = env.get_state()

        while state is not None:
            env.refresh()
            # env.set_action(actions.LEFT)
            exp = env.refresh_snake()

            state = exp.next_state

    pygame.quit()


if __name__ == '__main__':
    main()


