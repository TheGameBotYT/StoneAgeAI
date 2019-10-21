import numpy as np


class StoneAgeGame(object):

    def __init__(self, policy, player_types):
        # TODO: Keep food limit in mind for the GUI
        # TODO: Clean this in initialization
        self.placements_max = {'Farm': 1, 'Mating': 2, 'Wood': 7, 'Food': 20}
        self.spots_to_index = {'Farm': 0, 'Mating': 1, 'Wood': 2, 'Food': 3}
        self.spots = [[0] * x for x in self.placements_max.values()]
        #  self.meeple_player_sources = {1: 'red_meeple.png', 2: 'blue_meeple.png'}
        self.base_players = [1, 2]
        self.players = self.base_players.copy()
        self.player_types = player_types
        self.phase = 1
        self.round = 1
        self.current_player = np.random.choice(self.players)
        # print('Starting player: ', self.current_player)
        self.farms = [0, 0]
        self.meeples = [5, 5]
        self.food = [12, 12]
        self.points = [0, 0]
        self.placements = 5
        self.actions = 0
        self.states_list, self.action_list, self.reward_list = [], [], []
        self.policy = policy

    def track(self, state, choice, reward):
        """
        This functions tracks the S, A and R for the game.
        :param state: State before evolution
        :param choice: Choice made with the policy, state and possible actions
        :param reward: Reward gained from making choice in state
        :return:
        """
        # TODO: Only track the points of one player
        # TODO: Fix tracking on phase switches
        self.states_list.append(state)
        self.action_list.append(choice)
        self.reward_list.append(reward)

    def end_of_game(self):
        return self.round > 10

    def play(self, **kwargs):
        """
        This functions needs to work when this object is cast to the StoneAgeGUI-Class and allow for both player and AI
        :param self:
        :return:
        """
        state = self.get_state()
        if 'Choice' in kwargs:
            choice = kwargs['Choice']
        else:  # TODO: Might not work when AI has its turn and player presses
            possible_actions = self.check_possible_actions(state)
            choice = self.policy.take_choice(state, possible_actions)
        # print('CHOICE', choice)
        new_state, reward, done = self.step(choice)
        if done:
            # print('GAME OVER')
            highest_player = np.argmax(self.points)
            if self.points[0] > self.points[1]:
                reward += 100
            elif self.points[0] < self.points[1]:
                reward -= 100
            else:
                reward += 0
            # print(highest_player, ' HAS WON!!!')
        # print('NEW_STATE', new_state)
        self.track(state, choice, reward)
        # while not self.end_of_game():  # TODO: Used to be while for training

    def step(self, action):
        reward = 0
        # if self.current_player == 1:
        if self.phase == 1:  # Evolve state P1
            self.place_meeple(action)
        elif self.phase == 2:  # Evolve state P2
            self.take_action(action)
            # reward += self.take_action(action)
        # print('Reward after own', reward)
        # TODO: Do something about commenting/uncommenting below when playing/training
        """
        while self.current_player == 2:
            # Opponent using same policy
            state = self.get_state()
            possible_actions = self.check_possible_actions(state)
            action = self.policy.take_choice(state, possible_actions)
            # print('Chosen Action opponent by policy', action)
            if self.phase == 1:  # Evolve state P1
                self.place_meeple(action)
                reward -= 0
            elif self.phase == 2:  # Evolve state P2
                opponent_reward = self.take_action(action)
                # print('Current player in current player == 2 and self.phase == 2', self.current_player)
                # print('Opponent reward', opponent_reward)
                reward += -1*opponent_reward

        # print('Reward before return', reward)
        """
        return self.get_state(), reward, self.end_of_game()

    def get_state(self):
        """
        Make this into dict otherwise impossible to find
        :return: State of the game
        """
        # Future: Use game state to make GUI
        board_states = []
        if self.current_player == 1:
            self_ind = 0
            opp_ind = 1
            for player in [1, 2]:
                board_states.extend([self.spots[choice].count(player) for choice in range(0, 4)])
        elif self.current_player == 2:
            self_ind = 1
            opp_ind = 0
            for player in [2, 1]:
                board_states.extend([self.spots[choice].count(player) for choice in range(0, 4)])
        # 'Round': self.round,
        # 'Player': self.current_player,
        # 'Phase': self.phase
        state = {'Placements': self.placements, 'Actions': self.actions,
                 'SFood': self.food_state_encoding(self_ind), 'OFood': self.food_state_encoding(opp_ind),
                 'SelfAgri': self.farms[self_ind], 'OppAgri': self.farms[opp_ind],
                 'SelfWorkers': self.meeples[self_ind], 'OppWorkers': self.meeples[opp_ind],
                 'SelfFarm': board_states[0], 'OppFarm': board_states[4],
                 'SelfHut': board_states[1], 'OppHut': board_states[5],
                 'SelfChop': board_states[2], 'OppChop': board_states[6],
                 'SelfHunt': board_states[3], 'OppHunt': board_states[7]}
        return state

    def food_state_encoding(self, ind):
        food = self.food[ind]
        if food < 4:
            food_code = 0
        elif food < 8:
            food_code = 1
        elif food < 12:
            food_code = 2
        else:
            food_code = 3
        return food_code

    def check_possible_actions(self, state):
        """
        Notes for this important function:
        - Implement the 'no-meeples-left' by simply auto-evolving upon reaching min placements or 'actions' (lifts?/takes?)
        If len(possible_states) == 0 -> evolve?
        """
        if self.phase == 1:
            actions = [0, 1, 2, 3]
            # Function for checking the patch is not 'full'
            if (state['SelfFarm'] + state['OppFarm']) == 1:
                actions.remove(0)
            if (state['SelfHut'] + state['OppHut']) == 2:
                actions.remove(1)
            if (state['SelfChop'] + state['OppChop']) == 7:
                actions.remove(2)
            # No restriction for food
            # TODO: Might want to let the game learn that there are no benefits here beyond 10.
            # Below try/except is because above might've already removed
            # TODO: Does this work for opposite now as well?
            if state['SelfFarm'] == 10:
                try:
                    actions.remove(0)
                except ValueError:
                    pass
            if state['SelfWorkers'] == 10:
                try:
                    actions.remove(1)
                except ValueError:
                    pass
        elif self.phase == 2:  # Make sure actions without meeples are not being picked
            # Function for checking where your meeples are, using spots!
            placement_counts = [self.spots[choice].count(self.current_player) for choice in range(0, 4)]
            actions = [action for action, placement_count in enumerate(placement_counts) if placement_count != 0]
        else:
            raise Exception
        return actions

    def place_meeple(self, choice):
        if self.placements > 0:
            sub_spots = self.spots[choice]  # List of fills with that choice
            if 0 in sub_spots:
                self.placements -= 1  # If meeple placeable -> 1 less placements
                first_zero_index = [i for i, x in enumerate(self.spots[choice]) if x == 0][0]
                self.spots[choice][first_zero_index] = self.current_player
            else:
                pass
            if self.placements == 0:
                self.evolve_phase()

    def take_action(self, choice):
        """
        Functions which counts the number of actions left for active player.
        Then counts the number of placements on different spots for the active player.
        If the actions is bigger than zero, these choices are put into actions, evolving game state.
        If actions are zero -> next phase
        :param choice: Chosen choice by policy
        """
        if self.actions > 0:
            placements = self.spots[choice].count(self.current_player)  # Number of meeples on that choice
            if placements > 0:
                #  self.reset_info()
                pass
            reward = self.evolve_state(choice, placements)
            if self.actions == 0:
                reward = self.evolve_phase()
        return reward

    def evolve_state(self, choice, placements):
        """
        Function which maps choice taken to evolutions in game state
        :param choice: Chosen choice by policy
        :param placements: Number of placements, since some choice are number of places dependent
        """
        if placements > 0:
            if choice == 0:
                farm_var = self.farms[self.current_player - 1]
                if farm_var < 10:
                    self.farms[self.current_player - 1] += 1
                else:
                    pass
            elif choice == 1:
                if placements == 2:
                    meeple_var = self.meeples[self.current_player - 1]
                    if meeple_var < 10:
                        self.meeples[self.current_player - 1] += 1
                    else:
                        pass
            elif choice == 2:
                self.points[self.current_player - 1] += placements
                if self.current_player == 1:
                    self.clean_action_source_spots(choice)
                    return placements
            elif choice == 3:
                self.food[self.current_player - 1] += placements
            self.clean_action_source_spots(choice)
            return 0
        else:
            #  self.info = "Can't take that action"
            pass

    def clean_action_source_spots(self, choice):
        self.actions -= 1
        self.spots[choice] = [0 if x == self.current_player else x for x in self.spots[choice]]

    def feed(self):
        self.food = [self.food[i] - self.meeples[i] + self.farms[i] for i, x in enumerate(self.food)]
        self.points = [self.points[i] - 10 if self.food[i] < 0 else self.points[i] for i, x in enumerate(self.food)]
        if self.food[0] < 0:
            reward = -10
        else:
            reward = 0
        if self.food[0] < 0:
            self.food[0] = 0
        if self.food[1] < 0:
            self.food[1] = 0
        return reward

    def evolve_phase(self):
        reward = 0
        self.players.remove(self.current_player)
        if len(self.players) > 0:
            self.current_player = self.players[0]
            if self.phase == 1:
                self.placements = self.meeples[self.current_player - 1]
            elif self.phase == 2:
                self.actions = sum(self.current_player in sub for sub in self.spots)
        else:
            self.phase += 1
            self.players = self.base_players.copy()
            self.current_player = self.players[0]
            self.actions = sum(self.current_player in sub for sub in self.spots)
            if self.phase == 3:
                reward = self.feed()
                self.phase = 1
                self.base_players = self.base_players[1:] + self.base_players[:1]
                self.round += 1
                self.players = self.base_players.copy()
                self.current_player = self.players[0]
                self.placements = self.meeples[self.current_player - 1]

        return reward
