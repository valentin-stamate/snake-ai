import random
import time
import numpy as np
from tkinter import Canvas, Tk

from game.state.actions import Actions
from game.state.cell_type import CellType
from game.state.experience import Experience


class SnakeGame:
    """
    Tanken and updated from: https://github.com/StamateValentin/Python-Project
    """
    snackbar_width = 0
    offset_x = 0
    offset_y = snackbar_width

    weight = 3
    refresh_rate = 30
    colors = {CellType.EMPTY: '#202020', CellType.SNAKE: '#ffffff', CellType.WALL: '#3862ab',
              CellType.FOOD: '#f54545'}

    move = False
    game_won = False
    game_end = False
    game_running = False

    score = 0
    best_score = 0

    # State
    possible_actions = Actions.actions
    last_action = Actions.NOTHING

    def __init__(self, window: Tk, canvas: Canvas, config, show_progress=True):
        self.canvas = canvas
        self.window = window
        self.rows = config['rows']
        self.columns = config['columns']
        self.width = int(canvas['width']) - self.offset_x
        self.height = int(canvas['height']) - self.offset_y
        self.box_width = self.width / self.columns
        self.box_height = self.height / self.rows
        self.show_progress = show_progress
        # Lambdas
        self.refresh = lambda x: 0

        self.board = SnakeGame.create_matrix(self.rows, self.columns)
        self.board_box = self.create_board(self.rows, self.columns)

        # self.walls = config['blocks']

        # Initialization
        self.snake = []
        self.food = []
        self.dir = []
        self.board_box = self.create_board(self.rows, self.columns)

        # Controls
        # self.window.bind('<Left>', lambda e: self.left())
        # self.window.bind('<Right>', lambda e: self.right())
        # self.window.bind('<Up>', lambda e: self.up())
        # self.window.bind('<Down>', lambda e: self.down())

    def register_callbacks(self, refresh):
        self.refresh = refresh

    def start(self):
        if self.game_running:
            return

        self.initialize_starting_state()
        self.pre_draw()

    def initialize_starting_state(self):
        self.game_running = True
        self.game_won = False
        self.game_end = False
        self.score = 0

        self.reset_matrix(self.board, CellType.EMPTY)

        # Initialising blocks
        # for block in self.walls:
        #     self.put_on_board(block, CellType.WALL)

        self.snake = [[0, 2], [0, 1], [0, 0]]
        self.food = []

        self.put_on_board(self.snake[0], CellType.SNAKE)
        self.put_on_board(self.snake[1], CellType.SNAKE)
        self.put_on_board(self.snake[2], CellType.SNAKE)
        self.dir = [1, 0]

        self.spawn_food()

    def pre_draw(self):
        while True:
            if self.game_end or self.game_won:
                self.update_max_score()
                break

            self.draw()
            time.sleep(1 / self.refresh_rate)

        self.game_running = False

        self.reset_matrix(self.board, CellType.EMPTY)
        self.draw_board()

    def draw(self):
        self.draw_board()

        self.refresh(self)
        self.move = False

    def draw_board(self):
        if not self.show_progress:
            return

        for i in range(self.rows):
            for j in range(self.columns):
                new_color = self.colors[self.board[i][j]]
                old_color = self.canvas.itemcget(self.board_box[i][j], 'fill')

                if new_color != old_color:
                    self.canvas.itemconfig(self.board_box[i][j], fill=new_color)

    def refresh_snake(self):
        """
        Refresh snake, and returns the experience tuple
        :return: (state, action, reward, newState)
        """
        current_state = self.current_state()
        reward = -0.1

        old_tail = self.snake[len(self.snake) - 1]

        new_block = [self.snake[0][0] + self.dir[1], self.snake[0][1] + self.dir[0]]

        action = self.last_action
        self.last_action = Actions.NOTHING

        # Check outside
        if self.block_outside(new_block) or self.wall_collision(new_block):
            self.game_end = True
            reward = -10
            return Experience(current_state, action, reward, None)

        self.snake.remove(old_tail)

        self.snake.insert(0, new_block)

        self.put_on_board(old_tail, CellType.EMPTY)
        self.put_on_board(new_block, CellType.SNAKE)

        # Check collision
        if self.snake_collision():
            self.game_end = True
            reward = -10
            return Experience(current_state, action, reward, None)

        # Check for food
        head = self.snake[0]

        if SnakeGame.equal_blocks(head, self.food):
            self.score += 1
            self.snake.append(old_tail)
            self.put_on_board(old_tail, CellType.SNAKE)

            self.spawn_food()

            reward = 50

        # Here is the new state based on the action taken
        new_state = self.current_state()

        self.last_action = Actions.NOTHING

        return Experience(current_state, action, reward, new_state)

    def wall_collision(self, head_block):
        i = head_block[0]
        j = head_block[1]

        return self.board[i][j] == CellType.WALL

    def snake_collision(self):
        head = self.snake[0]

        # Tail collision
        for i in range(1, len(self.snake)):
            if self.equal_blocks(head, self.snake[i]):
                return True

        return False

    def block_outside(self, block):
        i = block[0]
        j = block[1]
        return i == -1 or i == self.rows or j == -1 or j == self.columns

    def update_max_score(self):
        self.best_score = max(self.best_score, self.score)

    @staticmethod
    def equal_blocks(block_a, block_b):
        return block_a[0] == block_b[0] and block_a[1] == block_b[1]

    def put_on_board(self, block, cell_type):
        i = block[0]
        j = block[1]

        self.board[i][j] = cell_type

    def put_grid(self, canvas: Canvas, rows, columns):
        color = '#151515'
        wid = 1

        box_width = self.width / columns
        box_height = self.height / rows

        off_x = self.offset_x
        off_y = self.offset_y

        for i in range(rows + 1):
            canvas.create_line(off_x + 0, off_y + box_height * i, off_x + self.width, off_y + box_height * i,
                               fill=color, width=wid)

        for j in range(columns + 1):
            canvas.create_line(off_x + box_width * j, off_y + 0, off_x + box_width * j, off_y + self.height,
                               fill=color, width=wid)

    def rectangle_coords(self, block):
        i = block[0]
        j = block[1]

        off_x = self.offset_x
        off_y = self.offset_y

        return off_x + j * self.box_width, off_y + i * self.box_height, off_x + (j + 1) * self.box_width, off_y + (i + 1) * self.box_height

    def create_board(self, rows, columns):
        board = []

        for i in range(rows):
            board.append([])
            for j in range(columns):
                board[i].append(self.canvas.create_rectangle(self.rectangle_coords([i, j]),
                                                             fill=self.colors[CellType.EMPTY],
                                                             outline=self.colors[CellType.EMPTY], width=self.weight))

        return board

    def spawn_food(self):
        available_blocks = []

        for i in range(self.rows):
            for j in range(self.columns):
                if self.board[i][j] == CellType.EMPTY:
                    available_blocks.append([i, j])

        if len(available_blocks) == 0:
            self.game_won = True
            self.game_end = True
            return

        random_block = random.choice(available_blocks)
        self.food = random_block

        self.put_on_board(self.food, CellType.FOOD)

    @staticmethod
    def reset_matrix(matrix, value=0):
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                matrix[i][j] = value

    @staticmethod
    def create_matrix(rows, columns, default_value=0):
        a = []
        for i in range(rows):
            a.append(SnakeGame.create_list(columns, default_value))

        return a

    @staticmethod
    def create_list(length, default_value=0):
        v = []
        for i in range(length):
            v.append(default_value)

        return v

    def left(self):
        if self.move:
            return

        j = self.dir[0]
        i = self.dir[1]

        if j != 1:
            self.move = True
            j = -1
            i = 0

        self.dir = [j, i]
        self.last_action = Actions.LEFT

    def right(self):
        if self.move:
            return

        j = self.dir[0]
        i = self.dir[1]

        if j != -1:
            self.move = True
            j = 1
            i = 0

        self.dir = [j, i]
        self.last_action = Actions.RIGHT

    def up(self):
        if self.move:
            return

        j = self.dir[0]
        i = self.dir[1]

        if i != 1:
            self.move = True
            i = -1
            j = 0

        self.dir = [j, i]
        self.last_action = Actions.UP

    def down(self):
        if self.move:
            return

        j = self.dir[0]
        i = self.dir[1]

        if i != -1:
            self.move = True
            i = 1
            j = 0

        self.dir = [j, i]
        self.last_action = Actions.DOWN

    # State
    def current_state(self):
        return np.array(self.board, dtype='float32')

    def get_possible_actions(self):
        return self.possible_actions

    def make_action(self, action):
        if action == Actions.LEFT:
            self.left()

        if action == Actions.UP:
            self.up()

        if action == Actions.RIGHT:
            self.right()

        if action == Actions.DOWN:
            self.down()

        # Else, nothing
