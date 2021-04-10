"""
Implementation of Monte Carlo Tree Search. I will have to merge this with my Node class at some point, since they
serve overlapping purposes.

In process of being built, code will not currently run.
"""

import datetime as dt
import random
from math import sqrt, log
from queue import Queue
import time

EXPLORATION_FACTOR = 1
TURN_TIME = 25


class MCTSNode:

    def __init__(self, root_game, parent):

        self.game = root_game
        self.parent = parent
        self.visits = 0
        self.children = []
        self.N = 0
        self.Q = 0

    @staticmethod
    def create_potential_moves(node, move_color):
        """
        Add list of possible moves to game state.

        Parameters
        ----------
        node : MiniMaxNode
            Parent node of all potential moves
        move_color : char, optional
            Player color, G or W
        Returns
        -------
        return_li : list
            Children of that node
        """
        return_li = []

        if node.game.end:
            return return_li
        # Check both of the spaces occupied by the player
        for spot in [(i, j) for i in range(5) for j in range(5) if
                     node.game.board[i][j]['occupant'] == move_color]:
            i, j = spot
            # check each possible move

            for space in node.game.get_movable_spaces(game=node.game, space=(i, j)):

                new_game = node.game.game_deep_copy(node.game, move_color)
                new_game.select_worker(move_color, i, j)

                new_game.move_worker(space[0], space[1], auto=True)
                if new_game.end:
                    return_li.append(MCTSNode(root_game=new_game, parent=node))
                else:
                    # given a legal move, check for each possible build
                    for build in new_game.get_buildable_spaces(new_game, (new_game.col, new_game.row)):
                        build_game = new_game.game_deep_copy(new_game,
                                                             new_game.color)

                        build_game.build_level(build[0], build[1], auto=True)
                        build_game.is_winning_move()
                        return_li.append(MCTSNode(root_game=build_game, parent=node))

        return return_li

    @property
    def mcts_score(self, exploration_factor=EXPLORATION_FACTOR):
        """Upper confidence bound for this node

        Attributes
        ----------
        exploration_factor : float
            Tradeoff between exploring new nodes and exploring those with high win rates
        """
        if self.N == 0:  # what to do if node hasn't been visited
            return float('inf')
        else:
            if self.parent is not None:
                return self.Q / self.N + exploration_factor * sqrt(2 * log(self.parent.N) / self.N)
            else:
                return self.Q / self.N + exploration_factor * sqrt(2 * log(1) / self.N)


class TreeSearch:

    def __init__(self, root_game):
        self.root_game = root_game.game_deep_copy(root_game, root_game.color)
        self.root = MCTSNode(self.root_game, None)
        self.run_time_seconds = 0
        self.num_nodes = 0
        self.num_rollouts = 0

    def search_tree(self, max_seconds=TURN_TIME):
        """
        Search children nodes of tree.

        Parameters
        ----------
        max_seconds : int
            Amount of seconds MCTS algorithm searches for the best move.
        """
        start_time = dt.datetime.now()
        current_time = dt.datetime.now()
        num_rollouts = 0
        while (current_time - start_time).total_seconds() < max_seconds:
            node, root_game = self.choose_simulation_node()
            winning_color = self.simulate_random_game(root_game)
            self.update_node_info(node, winning_color)
            num_rollouts += 1
            current_time = dt.datetime.now()

        self.run_time_seconds = (current_time - start_time).total_seconds()
        self.num_rollouts = num_rollouts

    def choose_simulation_node(self):
        """Choose a node from which to simulate a game"""
        node = self.root
        root_game = self.root_game.game_deep_copy(self.root_game, self.root_game.color)
        max_score = float('-inf')
        max_child_list = []

        # i = 0  # here to cut off potential endless loops
        # loop through potential children until we find a leaf node that doesn't permit further turns
        while len(node.children) > 0:
            for child in node.children:
                current_score = node.mcts_score
                if current_score > max_score:
                    max_child_list = [child]
                    max_score = current_score
                elif current_score == max_score:
                    max_child_list.append(child)
                # i += 1
            node = random.choice(max_child_list)

            root_game = self.root_game.game_deep_copy(node.game, node.game.color)

            if node.N == 0:
                return node, root_game

        if self.add_children_to_game_tree(node, root_game):
            node = random.choice(node.children)
            root_game = self.root_game.game_deep_copy(node.game, node.game.color)

        return node, root_game

    @staticmethod
    def add_children_to_game_tree(parent, root_game):
        """
        Create children of parent node, add them to game tree.
        "Expand" in MCTS terminology

        Returns
        -------
            bool: false if the game is over
        """

        if root_game.end:
            # don't expand a finished game
            return False

        potential_moves = parent.create_potential_moves(parent, root_game.color)

        if len(potential_moves) == 0:
            return False

        child_node_list = []
        for move in potential_moves:
            child_node_list.append(MCTSNode(root_game=move.game, parent=parent))

        parent.children = child_node_list
        return True

    @staticmethod
    def simulate_random_game(root_game):
        """
        Find winner of simulated game
        Called 'rollout' in Monte Carlo Tree Search terminology

        This function currently has an awful control structure. Will fix after further testing.
        Attributes
        ----------
            root_game : Game object

        Returns
        -------
            char : color that won the game
        """

        # Initialize variables pre-loop to avoid terminal node related errors
        temp_node = MCTSNode(root_game=root_game, parent=None)
        potential_game_list = temp_node.create_potential_moves(temp_node, root_game.color)

        # If no children, the game is done
        if len(potential_game_list) == 0:
            return root_game.color

        # Select the first game choice before the loop
        game_choice = random.choice(potential_game_list).game
        root_game = root_game.game_deep_copy(game_choice, game_choice.color)

        # Play the game until we find a winner
        while not root_game.end:
            temp_node = MCTSNode(root_game=root_game, parent=temp_node)
            potential_game_list = temp_node.create_potential_moves(temp_node, root_game.color)
            list_size = len(potential_game_list)

            if list_size == 0:  # this indicates we have reached the end of a game
                return root_game.get_opponent_color(root_game.color)
            else:
                rand_int = random.randint(0, list_size - 1)
                game_choice = potential_game_list[rand_int].game
                if game_choice.end:
                    return game_choice.color
                else:
                    root_game = root_game.game_deep_copy(game_choice, game_choice.color)
                    root_game.color = root_game.get_opponent_color(root_game.color)

    @staticmethod
    def update_node_info(node, outcome):
        reward = int(outcome == node.game.color)
        while node is not None:
            node.N += 1
            node.Q += reward
            node = node.parent  # traverse up the tree
            reward = int(not reward)  # switch reward for other color

    def get_best_move(self):
        """
        Get the best move in the current tree

        Returns
        -------
            Game : best move, ie highest N
        """
        max_node_list = []
        max_node_score = float('-inf')
        if self.root_game.end:
            return None

        for child in self.root.children:
            if child.mcts_score > max_node_score:
                max_node_list = [child]
                max_node_score = child.mcts_score
            elif child.mcts_score == max_node_score:
                max_node_list.append(child)

        return random.choice(max_node_list)

    def get_tree_size(self):
        node_queue = Queue()
        num_of_children = 0
        node_queue.put(self.root_game)
        while not node_queue.empty():
            current_node = node_queue.get()
            num_of_children += 1
            for child in current_node.children:
                node_queue.put(child)

        return num_of_children