"""
Implementation of Monte Carlo Tree Search. I will have to merge this with my Node class at some point, since they
serve overlapping purposes.

In process of being built, code will not currently run.
"""

import datetime as dt
import random
from math import sqrt, log
from queue import Queue

from game import game_deep_copy, create_potential_moves


class MCTSNode:

    def __init__(self, game, parent):

        self.game = game
        self.parent = parent
        self.visits = 0
        self.children = []
        self.N = 0
        self.Q = 0
        self.outcome = 0

    def create_potential_moves(self):
        self.children = create_potential_moves(self.game, self.game.color, self.game.color)

    def value(self, exploration_factor):
        """Upper confidence bound for this node

        Attributes
        ----------
        exploration_factor : float
            Tradeoff between exploring new nodes and exploring those with high win rates
        """
        if self.N == 0:  # what to do if node hasn't been visited
            return float('inf')
        else:
            return self.Q / self.N + exploration_factor * sqrt(2 * log(self.parent.N) / self.N)


class TreeSearch:

    def __init__(self, game):
        self.node_count = self.get_tree_size()
        self.root_game = game_deep_copy(game, game.color)
        self.root = MCTSNode(game = self.root_game, parent = None)
        self.run_time_seconds = 0
        self.num_nodes = 0
        self.num_rollouts = 0

    # currently using placeholder function for "values", func will get
    # value of each child in node

    def search_tree(self, max_seconds=60):
        """
        Search children nodes of tree.
        """
        start_time = dt.datetime.now()
        current_time = dt.datetime.now()
        num_rollouts = 0
        while (current_time - start_time).total_seconds() < max_seconds:
            node, game = self.choose_simulation_node()
            turn = game.turn()
            outcome = self.simulate_random_game(game)
            self.update_node_info(node, turn, outcome)
            num_rollouts += 1
            current_time = dt.datetime.now()

        self.run_time_seconds = (current_time - start_time).total_seconds()
        self.num_rollouts = num_rollouts

    def choose_simulation_node(self):
        """
        Choose the node to simulate from
        """
        node = self.root
        game = game_deep_copy(self.root_game, self.root_game.color)
        max_score = float('-inf')
        max_child_list = []

        while len(node.children) > 0:

            for child in node.children:
                current_score = node.game.get_board_score(self.game.color)
                if current_score >= max_score:
                    max_child_list.append(child)

            # obtain list of nodes with max value, pick one randomly
            node = random.choice(max_child_list)
            game = game_deep_copy(node.game, node.game.color)

            if node.N == 0:
                return node, game

        if self.add_children_to_game_tree(node, game):
            node = random.choice(node.children)
            game = game_deep_copy(node.game, node.game.color)

        return node, game

    @staticmethod
    def add_children_to_game_tree(parent, game):
        """
        Create children of parent node, add them to game tree

        Returns
        -------
            bool: false if the game is over
        """
        children_list = []
        if game.end:
            # don't expand a finished game
            return False

        for game in create_potential_moves(game, game.color, game.color):
            children_list.append(MCTSNode(game, parent))

        parent.children = children_list
        return True

    @staticmethod
    def simulate_random_game(game):
        """
        Called 'roll out' in Monte Carlo Tree Search terminology

        Attributes
        ----------
            game : Game object

        Returns
        -------
            char : color that won the game
        """

        moves = game.get_moves()  # placeholder, get_moves() is note defined

        while not game.end:
            move = random.choice(moves)
            game.play(move)
            moves.remove(move)

        return game.color

    @staticmethod
    def update_node_info(node, turn, outcome):

        reward = 0 if outcome == turn else 1

        while node is not None:
            node.N += 1
            node.Q += reward
            node = node.parent  # traverse up the tree
            reward = 0 if reward == 1 else 1

    def get_best_move(self):
        """
        Get the best move in the current tree

        Returns
        -------
            Game : best move, ie highest N
        """

        if not self.root_game.end:
            return None

        max_score = max(self.root.children.values())
        max_nodes = [n for n in self.root.children.values() if n.N == max_score]
        return random.choice(max_nodes)

    def get_tree_size(self):
        node_queue = Queue()
        num_of_children = 0
        node_queue.put(self.root)
        while not node_queue.empty():
            current_node = node_queue.get()
            num_of_children += 1
            for child in current_node.children.values():
                node_queue.put(child)

        return num_of_children
