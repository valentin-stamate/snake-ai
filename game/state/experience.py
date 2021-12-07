class Experience:
    def __init__(self, state, action, reward, next_state):
        self.state = state
        self.action = action
        self.reward = reward
        self.next_state = next_state

    def __str__(self):
        return f'State={self.state}\nAction={self.action}\nReward={self.reward}\nNextState={self.next_state}\n'
