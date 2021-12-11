import random
import threading
import tkinter as tk

import numpy as np

from game.snakegame import SnakeGame
from game.json_reader import JsonReader
from replay import ReplayMemory

from tensorflow import keras
from tensorflow.keras import models, layers
from keras import models
from tensorflow.keras import activations, losses

episodes = 100000
window = tk.Tk()

config = JsonReader.read('configuration.json')

replay_memory = ReplayMemory(500, 700)

lr = 0.01
df = 0.95

eps = 1
eps_step = 0.9995

rows = config['rows']
columns = config['columns']

nn = models.Sequential([
    layers.Dense(256, activation=activations.relu, input_shape=(rows * columns,)),
    layers.Dense(128, activation=activations.relu),
    layers.Dense(64, activation=activations.relu),
    layers.Dense(5, activation=activations.linear)
])

nn.compile(optimizer='rmsprop', loss=losses.MeanSquaredError(), metrics=['accuracy'])


def as_np_array(obj):
    """
    It should receve a list of objects
    """
    return np.array(obj).reshape(len(obj), rows * columns)


def main():
    global config

    window.title('Snake')

    canvas = tk.Canvas(window, bg="#202020", width=config['width'], height=config['height'])
    canvas.grid(row=0, column=0, columnspan=1)

    game = SnakeGame(window=window, canvas=canvas, config=config, show_progress=True)

    game.register_callbacks(lambda x: on_refresh(x))

    # Create a new thread to run the game independently
    threading.Thread(target=lambda: start(game)).start()

    window.eval('tk::PlaceWindow . center')
    window.mainloop()


def start(game: SnakeGame):
    for i in range(episodes):
        print(f"Episode {i + 1}")

        if i % 1000 == 0:
            nn.save('model')

        game.show_progress = False
        if i % 10 == 0:
            game.show_progress = True

        global last_state, step
        last_state = None
        step = 0

        game.start()

        if replay_memory.can_sample():
            print("Training")
            _input = []
            _target = []

            sample = replay_memory.sample()

            _input_next = []
            _input_map = []
            actions = []
            q_values_next = []
            rewards = []
            for j in range(len(sample)):
                exp = sample[j]
                state, action, reward, next_state = exp.as_tuple()

                _input.append(state)
                actions.append(action)

                rewards.append(reward)

                q_values_next.append(0)

                if next_state is not None:
                    _input_next.append(next_state)
                    _input_map.append(j)

            _input = np.asarray(_input, dtype='float32').reshape(len(_input), rows * columns) / 3
            _outputs = nn.predict(_input)
            q_current = np.amax(_outputs, axis=1)

            _input_next = np.asarray(_input_next, dtype='float32').reshape(len(_input_next), rows * columns) / 3
            _outputs_next = nn.predict(_input_next)
            q_next = np.amax(_outputs_next, axis=1)

            for j in range(len(_input_map)):
                ind = _input_map[j]
                q_values_next[ind] = q_next[j]

            _target = np.array(_outputs, copy=True)
            for j in range(len(_target)):
                _target[j][actions[j]] = q_current[j] * (1 - lr) + lr * (rewards[j] + df * q_values_next[j])

            nn.fit(_input, _target, epochs=2, batch_size=20, verbose=0)

            # for exp in replay_memory.sample():
            #     state, action, reward, next_state = exp.as_tuple()
            #
            #     _output = nn.predict(as_np_array([state]) / 3)[0]
            #     q_value = max(_output)
            #     action = np.argmax(_output)
            #
            #     q_value_next = 0
            #     if next_state is not None:
            #         q_value_next = max(nn.predict(as_np_array([next_state]))[0])
            #
            #     q_target = (1 - lr) * q_value + lr * (reward + disc_fact * q_value_next)
            #
            #     _output[action] = q_target
            #
            #     _input.append(state)
            #     _target.append(_output)
            #
            # _input = np.asarray(_input, dtype='float32').reshape(len(_input), 100) / 3
            # _target = np.asarray(_target, dtype='float32')
            # nn.fit(_input, _target, epochs=5, batch_size=10)

    window.destroy()


last_state = None
step = 0


def on_episode_end(episode):
    print(f'Episode %-3d ended' % episode)


def on_refresh(game: SnakeGame):

    global last_state, step
    step += 1
    # print(step)
    if last_state is None:
        experience = game.refresh_snake()
        replay_memory.push(experience)
        last_state = experience.state
        return

    rand = random.random()

    _output = nn.predict(as_np_array([last_state]))[0]
    action = np.argmax(_output)

    global eps
    if rand < eps:
        action = random.sample(game.possible_actions, 1)[0]
        # print("Random Move")

    if eps > 0.01:
        eps *= eps_step

    rnd = random.random()

    if rnd < 0.001:
        action = random.sample(game.possible_actions, 1)[0]
        # print("Random Move")

    game.make_action(action)
    experience = game.refresh_snake()
    replay_memory.push(experience)

    last_state = experience.next_state


if __name__ == '__main__':
    main()


