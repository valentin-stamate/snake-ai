from random import sample

import numpy as np
import pygame

from game.Experience import Experience


class Direction:
    LEFT = 0
    UP = 1
    RIGHT = 2
    DOWN = 3

    # [[i, j]]
    coords = [[0, -1], [-1, 0], [0, 1], [1, 0]]
    directions = [LEFT, UP, RIGHT, DOWN]


class CellType:
    EMPTY = 0
    SNAKE = 1
    HEAD = 2
    WALL = 3
    FOOD = 4


class Colors:
    colors = {CellType.EMPTY: '#202020',
              CellType.SNAKE: '#ffffff',
              CellType.HEAD: '#101010',
              CellType.WALL: '#3862ab',
              CellType.FOOD: '#f54545'}


class SnakeGame:
    move = False

    state = np.array([])
    food = []
    snake = []

    colors = Colors.colors
    direction = 0

    coords = Direction.coords

    def __init__(self, width, height, rows, columns, speed=20):
        self.width = width
        self.height = height
        self.rows = rows
        self.columns = columns
        self.speed = speed

        self.block_w = int(width / columns)
        self.block_h = int(height / rows)

        self.display = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Snake AI')

        self.clock = pygame.time.Clock()

        self.reset()

    def reset(self):
        self.initialize_state()

        self.direction = Direction.RIGHT
        self.snake = [[2, 3], [2, 2], [1, 2]]

        for i in range(len(self.snake)):
            c = self.snake[i]

            if i == 0:
                self.put(c, CellType.HEAD)
                continue

            self.put(c, CellType.SNAKE)

        self.spawn_food()

    def refresh(self):
        self.user_input()

        self.display.fill('#202020')

        for i in range(self.rows):
            for j in range(self.columns):
                color = self.colors[self.state[i, j]]
                rectangle = pygame.Rect(i * self.block_h, j * self.block_w, self.block_w, self.block_h)

                pygame.draw.rect(self.display, color, rectangle)

        pygame.display.flip()
        self.clock.tick(self.speed)

    def refresh_snake(self):
        """
        Refresh snake, and returns the experience tuple
        :return: (state, action, reward, newState)
        """
        state = np.array(self.state, copy=True)
        head = self.snake[0]
        food = self.food

        bottom = self.snake[len(self.snake) - 1]

        _dir = self.coords[self.direction]

        new_head = [head[0] + _dir[1], head[1] + _dir[0]]

        # Check outside
        if self.outside(new_head):
            return Experience(state, 0, 0, None)

        self.snake.remove(bottom)
        self.snake.insert(0, new_head)

        self.put(bottom, CellType.EMPTY)
        self.put(new_head, CellType.HEAD)
        self.put(head, CellType.SNAKE)

        # Check collision
        if self.snake_collision():
            return Experience(state, 0, 0, None)

        # Check for food

        if SnakeGame.equal(new_head, food):
            self.snake.append(bottom)
            self.put(bottom, CellType.SNAKE)

            self.spawn_food()

        new_state = np.array(state, copy=True)

        self.move = False
        return Experience(state, 0, 0, new_state)

    # Util
    @staticmethod
    def equal(block_a, block_b):
        return block_a[0] == block_b[0] and block_a[1] == block_b[1]

    def user_input(self):
        """Get User Input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.left()
                elif event.key == pygame.K_RIGHT:
                    self.right()
                elif event.key == pygame.K_UP:
                    self.up()
                elif event.key == pygame.K_DOWN:
                    self.down()

    def put(self, block, _type):
        self.state[block[0], block[1]] = _type

    def spawn_food(self):
        available_blocks = []

        for i in range(self.rows):
            for j in range(self.columns):
                if self.state[i, j] == CellType.EMPTY:
                    available_blocks.append([i, j])

        # TODO
        # if len(available_blocks) == 0:
        #     return

        random_block = sample(available_blocks, 1)[0]
        self.food = random_block

        self.put(self.food, CellType.FOOD)

    # Collisions
    def outside(self, block):
        i = block[0]
        j = block[1]
        return i == -1 or i == self.rows or j == -1 or j == self.columns

    def snake_collision(self):
        head = self.snake[0]

        # Tail collision
        for i in range(1, len(self.snake)):
            if self.equal(head, self.snake[i]):
                return True

        return False

    # Movement
    def left(self):
        if self.move:
            return

        if self.direction == Direction.RIGHT:
            return

        self.move = True
        self.direction = Direction.LEFT

    def right(self):
        if self.move:
            return

        if self.direction == Direction.LEFT:
            return

        self.move = True
        self.direction = Direction.RIGHT

    def up(self):
        if self.move:
            return

        if self.direction == Direction.DOWN:
            return

        self.move = True
        self.direction = Direction.UP

    def down(self):
        if self.move:
            return

        if self.direction == Direction.UP:
            return

        self.move = True
        self.direction = Direction.DOWN

    # Initial State
    def initialize_state(self):
        self.state = np.zeros((self.rows, self.columns), dtype='int32')
