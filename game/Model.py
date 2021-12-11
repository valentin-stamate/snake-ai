import numpy as np
from tensorflow import keras
from tensorflow.keras import models, layers
from keras import models
from tensorflow.keras import activations, losses

from game import ReplayMemory


class Model:

    def __init__(self):
        self.model = models.Sequential([
            layers.Dense(256, activation=activations.relu, input_shape=(11,)),
            layers.Dense(4, activation=activations.linear),
        ])

        self.model.compile(optimizer='adam', loss=losses.MeanSquaredError(), metrics=['accuracy'])
        pass

    def feed(self, states):
        _input = np.array(states, dtype='int32').reshape(len(states), 11)
        return self.model.predict(_input)

    def train(self, memory: ReplayMemory, gamma):
        print("Training")
        states, actions, rewards, new_states = memory.sample()

        states = np.array(states, dtype='float32')
        actions = np.array(actions, dtype='int32')
        rewards = np.array(rewards, dtype='float32')

        # Q Values For State(t)
        q = self.model.predict(states)

        mp = []
        q_new = []
        next_valid_states = []
        for i in range(len(new_states)):
            state = new_states[i]

            q_new.append(0)

            if state is not None:
                mp.append(i)
                next_valid_states.append(state)

        next_valid_states = np.asarray(next_valid_states)

        # Q Values For State S(t + 1)
        q_next = np.amax(self.model.predict(next_valid_states), axis=1)

        for i in range(len(mp)):
            ind = mp[i]
            q_new[ind] = q_next[i]

        q_new = np.array(q_new)
        q_new = rewards + q_new * gamma

        q_target = np.array(q, copy=True)

        np.put_along_axis(q_target, actions[:, None], q_new[:, None], axis=1)

        self.model.fit(states, q_target, epochs=3, batch_size=15, verbose=0)

    def save(self):
        self.model.save('model')

    def load(self):
        pass
