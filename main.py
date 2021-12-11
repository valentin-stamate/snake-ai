import time

import pygame

from game.SnakeGame import SnakeGame


def main():
    pygame.init()

    env = SnakeGame(600, 600, 10, 10, 10)
    while True:
        env.refresh()
        env.refresh_snake()

    pygame.quit()


if __name__ == '__main__':
    main()


