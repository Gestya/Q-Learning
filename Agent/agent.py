import threading
import json
import enum
import collections
from random import random

# My stuff
from world import World
from world import QValue


# Global const
ROW = 'row'
COL = 'col'


class Agent(threading.Thread):

    class State(enum.Enum):
        IDLE = 0,
        WAIT_FOR_ACTION = 1,
        WAIT_FOR_RESPONSE = 2,
        GAME_OVER = 3

    def __init__(self, msg_queue, event):
        threading.Thread.__init__(self)
        print('Start agent`s thread')

        self.msg_queue = msg_queue
        self.stopped = event

        self.world = World()
        self.fps = 5
        self.state = Agent.State.IDLE

        self.update_queue = collections.deque()

        # --- Q-Learning
        self.epsilon = 1.0
        self.alpha = 0.3         # ?
        self.gamma = 0.9         # ?
        self.latter_action = ''  # It's the action which has been done on the last step so far
        self.latter_position = {ROW: -1, COL: -1}

        self.parsers = {
            'world': self.__parse_world,
            'response': self.__parse_response
        }

        # --- D - E - B - U - G ----------------------
        self.i = 0
        self.actions = ['left', 'left', 'left', 'up', 'up', 'up', 'up', 'right', 'right', 'right']

    def get_world(self):
        return self.world

    def get_epsilon(self):
        return self.epsilon

    def set_epsilon(self, epsilon):
        self.epsilon = epsilon

    def run(self):
        while not self.stopped.wait(1.0 / self.fps):
            message = self.msg_queue.pop_from_inbox()
            if message:
                self.process_inbox(message)

            if self.state == Agent.State.WAIT_FOR_ACTION:
                print('.AGENT..WAIT_FOR_ACTION')
                assert self.world.is_going()
                self.__do_action()
            elif self.state == Agent.State.WAIT_FOR_RESPONSE:
                print('.AGENT..WAIT_FOR_RESPONSE')
                assert self.world.is_going()
            elif self.state == Agent.State.GAME_OVER:
                print('.AGENT..GAME_OVER')
                self.__do_restart()
            else:
                print('.AGENT..IDLE')

    def process_inbox(self, message):
        dictionary = json.loads(message)
        for key, value in dictionary.items():
            print(f'.AGENT. :: key={key}, val={value}')
            self.parsers[key](value)

    def __parse_world(self, value):
        self.world.parse_world(value)
        if self.world.is_going():
            self.state = Agent.State.WAIT_FOR_ACTION
            self.latter_position = self.world.get_position()

    def __parse_response(self, value):
        self.world.parse_response(value)
        if not self.world.is_going():
            self.state = Agent.State.GAME_OVER
            # UI update
            self.__update_ui(self.world.get_position(), 'x', self.world.get_reward(), True)
        else:
            self.state = Agent.State.WAIT_FOR_ACTION

        # Recalculate Q-Value
        value = self.__recalculate_qvalue()
        # UI update
        self.__update_ui(self.latter_position, self.latter_action, value, False)
        # Remember a new position
        self.latter_position = self.world.get_position()

    def __recalculate_qvalue(self):
        print('.AGENT.  ---> ', self.latter_position, self.world.get_position(), self.world.get_reward())
        new_q = self.world.get_qvalue(self.world.get_position())
        max_action, max_value = new_q.max_key_value()
        print('.AGENT.  --->  MAX (k,v) ', max_action, max_value)
        sample = self.world.get_reward() + self.gamma * max_value
        q = self.world.get_qvalue(self.latter_position)
        v = (1.0 - self.alpha) * q.values[self.latter_action] + self.alpha * sample
        q.values[self.latter_action] = v
        self.world.set_qvalue(self.latter_position, q)
        print('.AGENT.  --->  New Value ', v)

        return v

    def __do_action(self):
        # --- D - E - B - U - G -----------------------------
        # self.latter_action = self.actions[self.i]
        # self.i += 1
        # --- N - O - R - M - A - L -------------------------
        if random() < self.epsilon:
            self.latter_action = QValue.get_random_action()
            print('.AGENT.  --->  Random action ', self.latter_action)
        else:
            action, _ = self.world.get_qvalue(self.latter_position).max_key_value()
            self.latter_action = action
            print('.AGENT.  --->  The best action ', self.latter_action)

        # ---------------------------------------------------
        self.msg_queue.push_to_outbox('{"action" : "%s"}' % self.latter_action)
        self.state = Agent.State.WAIT_FOR_RESPONSE

    def __do_restart(self):
        self.msg_queue.push_to_outbox('{"command" : "restart"}')
        self.state = Agent.State.IDLE
        # --- D - E - B - U - G ----------------------
        self.i = 0

    def __update_ui(self, position, action, value, terminal):
        st = {
            'row': position[ROW],
            'col': position[COL],
            'action': action,
            'value': '{:.3f}'.format(value),
            'terminal': terminal,
        }
        if terminal:
            for a in ['left', 'up', 'right', 'down']:
                st['action'] = a
                self.update_queue.append(st.copy())
        else:
            self.update_queue.append(st)
