import random
from game.Experience import Experience
from game.Model import Model
from game.ReplayMemory import ReplayMemory
from game.SnakeGame import SnakeGame, Direction
import numpy as np
import pygame
import matplotlib.pyplot as plt


class Agent:
    eps = 1
    decay = 0.992

    gamma = 0.9

    def __init__(self):
        self.model = Model()
        self.rows = 20
        self.columns = 20
        self.input_size = self.rows * self.columns

        self.env = SnakeGame(400, 400, self.rows, self.columns, speed=60, user_control=False)
        self.actions = Direction.directions

        self.memory = ReplayMemory(750, 1000)

    def start(self):
        pygame.init()

        episodes = 10000
        env = self.env

        scores = []
        max_score = 0

        for i in range(episodes):
            print(f"Episode {i}")
            env.reset()

            state = env.get_state()
            while state is not None:
                env.refresh()

                action = self.action(state)
                env.set_action(action)

                raw_exp = env.refresh_snake()

                if raw_exp is None:
                    state = None
                    continue

                new_state = None
                if raw_exp.next_state is not None:
                    new_state = env.get_state()

                exp = Experience(state, action, raw_exp.reward, new_state)
                self.memory.push(exp)

                state = new_state

            if self.memory.can_sample():
                self.model.train(self.memory, self.gamma)

            scores.append(env.score)

            plt.plot(scores)
            plt.xlabel('Episode')
            plt.ylabel('Score')
            plt.show()

            # Save The Model
            old_score = max_score
            max_score = max(max_score, env.score)

            if old_score != max_score:
                self.model.save()

        pygame.quit()

    def action(self, state):
        action = np.argmax(self.model.feed([state])[0])

        rnd = random.random()
        if self.eps >= 0.01 and rnd < self.eps:
            action = random.sample(self.actions, 1)[0]

        if self.eps >= 0.01:
            self.eps *= self.decay

        return action
