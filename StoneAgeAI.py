import numpy as np
from collections import defaultdict
import pandas as pd
import time
from IPython.display import display

class GLIEMonteCarloControl(object):

    def __init__(self, filepath=None):
        if filepath is None:
            self.N = defaultdict(lambda: np.zeros(4))
            self.Q = defaultdict(lambda: np.zeros(4))
            self.epsilon = 1
            self.gamma = 1
        else:
            self.Q = pd.read_pickle(filepath).T
            self.epsilon = 0

    def update(self, states, actions, rewards, episode_number):
        if episode_number < 500000:
            self.epsilon = 1
        else:
            self.epsilon = 1/np.power(episode_number, 0.25)
        """
        if episode_number % 1000 == 0:
            print('Number of states at Episode: ' + str(episode_number), str(len(states)))
        if len(states) > 5000:
            S, A, R = pd.DataFrame(states), pd.DataFrame(actions), pd.DataFrame(rewards)
            S.to_pickle('StoneAgeS.p')
            A.to_pickle('StoneAgeA.p')
            R.to_pickle('StoneAgeR.p')
            raise
        """
        for i, state in enumerate(states):
            update_state = tuple(state.values())
            # update_state = tuple(update_state)
            self.N[update_state][actions[i]] += 1.0
            old_Q = self.Q[update_state][actions[i]]
            self.Q[update_state][actions[i]] = old_Q +\
                                               (sum(rewards[i:]) - old_Q) / self.N[update_state][actions[i]]

    def take_choice(self, state, possible_actions):
        if np.random.uniform() < self.epsilon:
            action = np.random.choice(possible_actions)
        else:
            state = tuple(state.values())
            try:
                q_values = self.Q.loc[state].values
                print('Using Policy')
                nan_filter = np.empty(len(q_values)) * np.nan
                nan_filter[possible_actions] = 1
                arr = np.array(q_values * nan_filter)
                action = np.nanargmax(arr)
            except KeyError: #  Never before seen state
                action = np.random.choice(possible_actions)
                print('Never seen before state: ', state)
        return action


class QLearning(object):

    def __init__(self, lr, gamma, epsilon, filepath=None):
        if filepath is None:
            self._N = defaultdict(lambda: defaultdict(lambda: 0))
            self._Q = defaultdict(lambda: defaultdict(lambda: 0))
            self.lr = lr
            self.gamma = gamma
            self.epsilon = epsilon
        else:
            self._Q = pd.read_pickle(filepath)
            self.epsilon = 0

    #TODO: Implement epsilon decay

    def update(self, state, action, reward, next_state):
        q_value = (1-self.lr) * self.get_qvalue(state, action) + \
            self.lr * (reward + self.gamma*self.get_value(next_state))

        self.set_qvalue(state, action, q_value)

    def get_qvalue(self, state, action):
        return self._Q[state][action]

    def set_qvalue(self, state, action, value):
        self._Q[state][action] = value

    def get_value(self, state, possible_actions):
        if len(possible_actions) == 0:
            return 0

        q_values = [self.get_qvalue(state, action) for action in possible_actions]
        value = np.max(q_values)
        return value

    def get_best_action(self, state, possible_actions):
        if len(possible_actions) == 0:
            return None

        q_values = [self.get_qvalue(state, action) for action in possible_actions]
        ind = np.argmax(q_values)
        best_action = possible_actions[ind]
        return best_action

    def take_choice(self, state, possible_actions):

        if len(possible_actions) == 0:
            return None

        if np.random.uniform() < self.epsilon:
            action = np.random.choice(possible_actions)
        else:
            action = self.get_best_action(state, possible_actions)

        return action


