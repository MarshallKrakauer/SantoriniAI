"""
Implementation of Monte Carlo Tree Search. I will have to merge this with my Node class at some point, since they
serve overlapping purposes.

In process of being build, code will not currently run.
"""

import datetime as dt
from math import sqrt, log
from game import Game, game_deep_copy


class MCTSNode:

    def __init__(self, move, parent):

        self.move = move
        self.parent = parent
        self.visits = 0
        self.Q_reward = 0
        self.Q_RAVE = 0
        self.children = []
        self.outcome = 0

    def create_potential_moves(self):
        pass  # placeholder, need to move function from game.py

    @property
    def value(self, explore):
        """Upper confidence bound for this node

        Attributes
        ----------
        explore : float
            Tradeoff between exploring new nodes and exploting those with high win rates
        """
        if self.N == 0:  # what to do if node hasn't been visited
            return float('inf')
        else:
            return self.Q / self.N + explore * sqrt(2 * log(self.parent.N) / self.N)

class TreeSearch:

    def __init__(self, game):
        self.root_state = game_deep_copy(game, game.color)
        self.root = MCTSNode()
        self.run_time_seconds = 0
        self.num_nodes = 0
        self.num_rollouts = 0

    def search(self, max_seconds = 60):

        start_time = dt.datetime.now()


def run_for_ten_seconds():
    """Testing setting a max time, some version of this will be used for Tree Search"""
    max_seconds = 10
    i = 0
    start_time = dt.datetime.now()
    current_time = dt.datetime.now()
    while (current_time - start_time).total_seconds() < max_seconds:
        current_time = dt.datetime.now()
        i += 1
        print(i)