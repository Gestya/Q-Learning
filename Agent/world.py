import enum
import math
from random import random


# Global const
ROW = 'row'
COL = 'col'


class QValue:
    actions = ['left', 'up', 'right', 'down']

    def __init__(self):
        self.values = {}
        for a in self.actions:
            self.values[a] = 0.0

    @staticmethod
    def get_random_action():
        f = random() * len(QValue.actions)
        i = math.floor(f)
        return QValue.actions[i]

    def max_key_value(self):
        max_k = 'left'
        max_v = self.values[max_k]
        for k, v in self.values.items():
            if v > max_v:
                max_v = v
                max_k = k
        return max_k, max_v


class World:

    class State(enum.Enum):
        NOT_EXIST = 0
        IS_GOING = 2
        WIN = 3
        LOSE = 4

        @staticmethod
        def get_state_by_string(string):
            if string == 'is_going':
                return World.State.IS_GOING
            elif string == 'win':
                return World.State.WIN
            elif string == 'lose':
                return World.State.LOSE
            else:
                assert False and 'Unknown world state'
                return World.State.NOT_EXIST

    def __init__(self):
        self.state = World.State.NOT_EXIST

        # --- Size of world (maze)
        self.width = 0
        self.height = 0

        # --- Bot's position
        self.position = {ROW: -1, COL: -1}

        # --- Reward (the last received reward)
        self.reward = 0

        # --- Grid of Q-Values
        self.grid = []

    def is_going(self):
        return self.state == World.State.IS_GOING

    def get_size(self):
        return self.height, self.width

    def get_position(self):
        return self.position.copy()

    def get_reward(self):
        return self.reward

    # --------------------------------------------
    #   QValue

    def get_qvalue(self, position):
        r = position[ROW]
        c = position[COL]
        return self.grid[r][c]

    def set_qvalue(self, position, qvalue):
        r = position[ROW]
        c = position[COL]
        self.grid[r][c] = qvalue

    # --------------------------------------------
    #   Parsers

    def parse_world(self, dictionary):
        print('## world ## parser ##')
        for key, value in dictionary.items():
            print(f"## world ## {key} : {value}")
            if key == 'width':
                self.width = int(value)
            elif key == 'height':
                self.height = int(value)
            elif key == 'row':
                self.position[ROW] = int(value)
            elif key == 'col':
                self.position[COL] = int(value)
            elif key == 'state':
                if value == 'just_created':
                    self.__create_grid()
                    value = 'is_going'
                assert value == 'is_going'
                self.state = World.State.get_state_by_string(value)
            else:
                assert False and 'Unknown JSON-key {world}'

        print('## world ## COMPLETE ##')

    def parse_response(self, dictionary):
        print('## response ## parser ##')
        for key, value in dictionary.items():
            print(f"## response ## {key} : {value}")
            if key == 'row':
                self.position[ROW] = int(value)
            elif key == 'col':
                self.position[COL] = int(value)
            elif key == 'reward':
                self.reward = float(value)
            elif key == 'state':
                self.state = World.State.get_state_by_string(value)
            else:
                assert False and 'Unknown JSON-key {response}'

        print('## response ## COMPLETE ##')

    def __create_grid(self):
        self.grid.clear()
        for i in range(self.height):
            self.grid.append([])
            for j in range(self.width):
                self.grid[i].append(QValue())
