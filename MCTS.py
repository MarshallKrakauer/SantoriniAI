"""
Implementation of Monte Carlo Tree Search. Currently working on improving early game moves.

In process of being built, code will not currently run.
"""

import datetime as dt
import random
from math import sqrt, log
from queue import Queue
import game

EXPLORATION_FACTOR = 1.4  # square root of 2
TURN_TIME = 30

# Global variable, stores list of moves with corresponding potential moves
# Exists to save time from hefty potential moves process
move_dict = {}

random.seed(dt.datetime.now().microsecond)  # set seed


class MCTSNode:

    def __init__(self, root_game, parent):

        self.game = root_game
        self.parent = parent
        self.children = []
        self.N = 0
        self.Q = 0

    def __repr__(self):
        if self.N == 0 or self.parent is None:
            return str(self.game) + self.game.color

        return (str(self.game) + self.game.color + '\n' + str(self.Q) + '/' + str(self.N) + ' '
                + str(round(100 * self.Q / self.N, 1)) +
                '%, score: ' + str(round(self.mcts_score, 6)))

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
        node.game.color = move_color
        potential_move_li = []
        if node.game.end:
            return potential_move_li
        try:
            moves = move_dict[node.game.dict_key_rep]
            temp_game = game.Game()
            return [MCTSNode(temp_game.get_dict_repr(move), parent=node) for move in iter(moves)]
        except KeyError:
            # Check both of the spaces occupied by the player
            for spot in [(i, j) for i in range(5) for j in range(5) if
                         node.game.board[i][j]['occupant'] == move_color]:
                i, j = spot
                # check each possible move
                for space in node.game.get_movable_spaces(game=node.game, space=(i, j)):
                    new_game = node.game.game_deep_copy(node.game, move_color)
                    new_game.select_worker(move_color, i, j)

                    new_game.move_worker(space[0], space[1], auto=True)

                    # If we find a winning moves, return only that
                    # As such, this assumes that a player will always make a winning move when possible
                    if new_game.is_winning_move():
                        potential_move_li = [MCTSNode(root_game=new_game, parent=node)]
                        move_dict[node.game.dict_key_rep] = [move.game.dict_repr for move in potential_move_li]
                        return potential_move_li
                    else:
                        # given a legal move, check for each possible build
                        for build in new_game.get_buildable_spaces(new_game, (new_game.col, new_game.row)):
                            build_game = new_game.game_deep_copy(new_game,
                                                                 new_game.color)

                            build_game.build_level(build[0], build[1], auto=True)

                            potential_move_li.append(MCTSNode(root_game=build_game, parent=node))
            move_dict[node.game.dict_key_rep] = [move.game.dict_repr for move in potential_move_li]
            return potential_move_li

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
            return self.Q / self.N + exploration_factor * sqrt(log(self.parent.N) / self.N)

    @staticmethod
    def choose_child_game(root_game, potential_game_list):
        """Choose child game in node simulation"""
        found_winning_move = False
        move_num = 0
        color = root_game.color
        game_choice = root_game
        while not found_winning_move and move_num < len(potential_game_list):
            curr_game = potential_game_list[move_num].game
            has_won = curr_game.is_winning_move(color)
            if has_won:
                found_winning_move = True
                game_choice = potential_game_list[move_num].game
                game_choice.end = True

            move_num += 1

        if not found_winning_move:
            game_choice = random.choice(potential_game_list).game

        return game_choice


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
        global move_dict
        move_dict = {}  # global variable reset every time we look for best node
        while num_rollouts < 5000 and (current_time - start_time).total_seconds() < max_seconds:
            node, root_game = self.choose_simulation_node()
            winning_color = self.simulate_random_game(node, root_game)
            self.update_node_info(node, winning_color)
            num_rollouts += 1
            current_time = dt.datetime.now()
        print("rollouts:", num_rollouts, 'moves', len(move_dict))
        self.run_time_seconds = (current_time - start_time).total_seconds()
        self.num_rollouts = num_rollouts

    def choose_simulation_node(self):
        """Choose a node from which to simulate a game"""
        node = self.root
        root_game = self.root_game.game_deep_copy(self.root_game, self.root_game.color)
        max_child_list = []

        # loop through potential children until we find a leaf node that doesn't permit further turns
        while len(node.children) > 0:
            max_score = float('-inf')
            for child in node.children:
                current_score = child.mcts_score
                if current_score > max_score:
                    max_child_list = [child]
                    max_score = current_score
                elif current_score == max_score:
                    max_child_list.append(child)

            # If multiple nodes have the max score, we randomly select one
            node = random.choice(max_child_list)

            # Switch to opponents turn
            node.game.color = node.game.opponent_color
            root_game = node.game.game_deep_copy(node.game, node.game.color)

            if node.N == 0:
                return node, root_game

        if self.add_children_to_game_tree(node, root_game):
            node = random.choice(node.children)

        # switch to opponents turn again
        node.game.color = node.game.opponent_color
        root_game = node.game.game_deep_copy(node.game, node.game.color)

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
    def simulate_random_game(node, root_game):
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
        root_game.color = root_game.opponent_color
        new_node = MCTSNode(root_game=root_game, parent=None)
        potential_game_list = new_node.create_potential_moves(node, node.game.opponent_color)

        # If no children, the game is done
        if len(potential_game_list) == 0 or node.game.end:
            return node.game.color

        while not root_game.end:
            list_size = len(potential_game_list)
            if list_size == 0:  # this indicates we have reached the end of a game
                return root_game.color
            else:
                game_choice = new_node.choose_child_game(root_game, potential_game_list)
                if game_choice.end:
                    return game_choice.color
                else:
                    root_game = root_game.game_deep_copy(game_choice, game_choice.color)
                    root_game.color = root_game.get_opponent_color(root_game.color)
                    new_node = MCTSNode(root_game=root_game, parent=node)
                    potential_game_list = new_node.create_potential_moves(new_node, root_game.color)

        return root_game.color

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
        max_node_score = 0
        if self.root_game.end:
            return None

        # Find child that was visited the most
        for child in self.root.children:
            current_score = child.N
            if current_score > max_node_score:
                max_node_list = [child]
                max_node_score = current_score
            elif current_score == max_node_score:
                max_node_list.append(child)

        game_choice = random.choice(max_node_list)

        try:
            if len(game_choice.children[0].children) > 0:
                print(self.root_game, game_choice, game_choice.children[0], game_choice.children[0].children[0])
            else:
                print(self.root_game, game_choice, game_choice.children[0])
        except:
            pass

        return game_choice

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
