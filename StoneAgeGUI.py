from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
import numpy as np
from StoneAgeGame import StoneAgeGame
from StoneAgeAI import GLIEMonteCarloControl
import time

Window.clearcolor = (0.3, 0.3, 0.3, 1)

policy = GLIEMonteCarloControl('Q2Mnewdowncast.p')

game_instance = StoneAgeGame(policy=policy, player_types=['Player', 'AI'])


class StoneAgeGUI(BoxLayout):

    def __init__(self, game):
        super(StoneAgeGUI, self).__init__()
        self.game = game
        self.meeple_image_ids = ['farm1', 'hut1', 'hut2', 'wood1', 'wood2', 'wood3',
                                 'wood4', 'wood5', 'wood6', 'wood7', 'food1', 'food2',
                                 'food3', 'food4', 'food5', 'food6', 'food7']
        self.orientation = 'vertical'
        food_space, wood_space, farm_space, hut_space = self.create_meeple_space()
        self.create_scoreboard()
        button_space = BoxLayout(id='static_space', orientation='horizontal', size_hint_y=0.1)
        self.add_widget(button_space)

        # Adding Meeple Image widgets
        self.meeple_group = []
        for i, label in enumerate(self.meeple_image_ids):
            meeple = MeepleImage(id=label, allow_stretch=True)
            if 'farm' in label:
                farm_space.add_widget(meeple)
            elif 'hut' in label:
                hut_space.add_widget(meeple)
            elif 'food' in label:
                food_space.add_widget(meeple)
            elif 'wood' in label:
                wood_space.add_widget(meeple)
            else:
                raise FutureWarning
            setattr(self, label, meeple)
            self.meeple_group.append(meeple)

        # Adding button widgets
        for i, label in enumerate(['farm_button', 'hut_button', 'wood_button', 'food_button']):
            button = Action(id=str(label), text="{}".format(label))
            button_space.add_widget(button)
            setattr(self, label, button)

    def create_meeple_space(self):
        meeple_space = BoxLayout(orientation='vertical')
        self.add_widget(meeple_space)
        food_wood_space = BoxLayout(orientation='horizontal', size_hint_y=0.7)
        farm_hut_space = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        meeple_space.add_widget(food_wood_space)
        meeple_space.add_widget(farm_hut_space)
        food_space = GridLayout(rows=2)
        wood_space = GridLayout(rows=2)
        food_wood_space.add_widget(food_space)
        food_wood_space.add_widget(wood_space)
        farm_space = GridLayout(rows=1)
        hut_space = GridLayout(rows=1)
        farm_hut_space.add_widget(farm_space)
        farm_hut_space.add_widget(hut_space)
        return food_space, wood_space, farm_space, hut_space

    def create_scoreboard(self):
        scoreboard = GridLayout(cols=2, size_hint_y=0.2)
        scoreboard_grp = []
        scoreboard_dict = self.get_scoreboard_values()
        for k, v in scoreboard_dict.items():
            item = Label(id=k, text=k+'  '+v, font_size=30)
            scoreboard.add_widget(item)
            scoreboard_grp.append(item)
        self.add_widget(scoreboard)
        self.scoreboard_grp = scoreboard_grp

    def get_scoreboard_values(self):
        scoreboard_vals = {'Round': str(self.game.round),
                           'Phase': str(self.game.phase),
                           'Score': ', '.join(map(str, self.game.points)),
                           'Food': ', '.join(map(str, self.game.food)),
                           'Farms': ', '.join(map(str, self.game.farms)),
                           'Meeples': ', '.join(map(str, self.game.meeples))}
        return scoreboard_vals

    def update(self, dt):
        """
        Skeleton for Stone Age GUI update widget.
        On a GUI update call needs to check AI or player
        If AI:
            'Play a turn' using policy
        Elif Player:
            While no touch:
                pass
            If touch:
                Resolve action based on touch input

        Evolve state if one of above succeeded
        Resolve GUI Widgets from new state
        :param action: determines if action is given by pressing a button
        :param dt:
        :return:
        """

        if self.game.player_types[self.game.current_player-1] == 'AI':
            self.game.play()
            time.sleep(1)
            self.update_gui()

        elif self.game.player_types[self.game.current_player-1] == 'Player':
            button_bools = [self.farm_button.touched, self.hut_button.touched,
                            self.wood_button.touched, self.food_button.touched]
            if any(button_bools):
                choice = [i for i, x in enumerate(button_bools) if x][0]
                self.game.play(**{'Choice': choice})
                self.reset_touched()
                self.update_gui()
            else:
                pass

    def update_gui(self):
        for meeple in self.meeple_group:
            label_spots = self.check_game_spots()
            meeple.show(label_spots[meeple.id])
        scoreboard_vals = self.get_scoreboard_values()
        for label in self.scoreboard_grp:
            label.text = label.id + '  ' + scoreboard_vals[label.id]

    def reset_touched(self):
        self.farm_button.touched = False
        self.hut_button.touched = False
        self.wood_button.touched = False
        self.food_button.touched = False

    def check_game_spots(self):
        game_spots = self.game.spots
        label_spots = {
            'farm1': game_spots[0][0],
            'hut1': game_spots[1][0],
            'hut2': game_spots[1][1],
            'wood1': game_spots[2][0],
            'wood2': game_spots[2][1],
            'wood3': game_spots[2][2],
            'wood4': game_spots[2][3],
            'wood5': game_spots[2][4],
            'wood6': game_spots[2][5],
            'wood7': game_spots[2][6],
            'food1': game_spots[3][0],
            'food2': game_spots[3][1],
            'food3': game_spots[3][2],
            'food4': game_spots[3][3],
            'food5': game_spots[3][4],
            'food6': game_spots[3][5],
            'food7': game_spots[3][6]
        }
        return label_spots


class MeepleImage(Image):

    def __init__(self, **kwargs):
        super(MeepleImage, self).__init__(**kwargs)
        self.source = 'trans.png'

    def show(self, source_int):
        """
        Functions which tells the meeple it should be visible or not and which colour
        :param source_int: Integer relating to the player playing
        """
        if source_int == 0:
            self.source = 'trans.png'
        elif source_int == 1:
            self.source = 'green_meeple.png'
        elif source_int == 2:
            self.source = 'red_meeple.png'


class Action(Button):

    def __init__(self, **kwargs):
        super(Action, self).__init__(**kwargs)
        self.font_size = 30
        self.color = [0, 1, 1, 0.5]
        self.touched = False
        self.action_dict = {'farm_button': 0,
                            'hut_button': 1,
                            'food_button': 2,
                            'wood_button': 3}

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.touched = True


class StoneAgeApp(App):

    def build(self):
        gui = StoneAgeGUI(game_instance)
        Clock.schedule_interval(gui.update, 30.0 / 60.0)
        return gui


app = StoneAgeApp()
app.run()

