"""
Implementation of Monte Carlo Tree Search. Currently working on improving early game moves.
"""

import datetime as dt
import random
from math import sqrt, log

EXPLORATION_FACTOR = 0.5  # square root of 2
TURN_TIME = 30

# Global variable, stores list of moves with corresponding potential moves
# Exists to save time from hefty potential moves process
move_dict = {}

random.seed(dt.datetime.now().microsecond)  # set seed

SPACE_LIST = [(i, j) for i in range(5) for j in range(5)]


class MCTSNode:

    def __init__(self, root_game, parent):

        self.game = root_game
        self.parent = parent
        self.children = []
        self.N = 0
        self.Q = 0
        self.deleted = False

    @property
    def heuristic_score(self):
        return self.game.get_height_score(self.game.color)

    def __repr__(self):
        if self.N == 0 or self.parent is None:
            return str(self.game) + self.game.color

        return (str(self.game) + self.game.color + '\n' + str(self.Q) + '/' + str(self.N) + ' '
                + str(round(100 * self.Q / self.N, 1)) +
                '%, score: ' + str(round(self.mcts_score, 6)))

    @staticmethod
    def create_potential_moves(node):
        """
        Add list of possible moves to game state.

        Parameters
        ----------
        node : MCTSNode
            Parent node of all potential moves
        Returns
        -------
        return_li : list
            Children of that node
        """
        potential_move_li = []

        # If the game is over, produce no children
        if node.game.winner is not None:
            return potential_move_li

        # Set the correct mover
        if (node.game.turn + 1) % 2 != 0:
            move_color = 'W'
        else:
            move_color = 'G'

        # Check both of the spaces occupied by the player
        for spot in [(i, j) for i in range(5) for j in range(5) if
                     node.game.board[i][j]['occupant'] == move_color]:

            i, j = spot
            # check each possible move
            for space in node.game.get_movable_spaces(game=node.game, space=(i, j)):

                # Move a copy of the game, as to not impact the game itself
                new_game = node.game.game_deep_copy(node.game, move_color)
                new_game.select_worker(move_color, i, j)

                # Since we have at least one legal move, we can change the color and turn
                new_game.color = move_color
                new_game.move_worker(space[0], space[1], auto=True)

                # If we find a winning moves, return only that
                # As such, this assumes that a player will always make a winning move when possible
                if new_game.is_winning_move():
                    potential_move_li = [MCTSNode(root_game=new_game, parent=node)]
                    new_game.winner = move_color
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

        if len(potential_move_li) == 0:
            node.game.winner = node.game.opponent_color

        return potential_move_li

    @property
    def mcts_score(self, exploration_factor=EXPLORATION_FACTOR, heuristic_factor=0.0):
        """Upper confidence bound for this node

        Attributes
        ----------
        exploration_factor : float
            Tradeoff between exploring new nodes and exploring those with high win rates
        """
        if self.N == 0:  # what to do if node hasn't been visited
            return float('inf')
        else:
            # Exploration (win rate) + exploitation + heuristic
            return (self.Q / self.N
                    + exploration_factor * sqrt(log(self.parent.N) / self.N)
                    # + heuristic_factor * self.game.get_minimax_score(self.game.color) / (self.game.turn + 1)
                    )

    def get_winning_color(self):
        for i, j in SPACE_LIST:
            if self.game.board[i][j]['level'] == 3:
                return self.game.board[i][j]['occupant']


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
            node = self.choose_simulation_node()
            simulation_game = node.game.game_deep_copy(node.game, node.game.color)
            winning_color = self.simulate_random_game(simulation_game)
            self.update_node_info(node, winning_color)
            num_rollouts += 1
            current_time = dt.datetime.now()
        print("rollouts:", num_rollouts, 'moves', len(move_dict))
        self.run_time_seconds = (current_time - start_time).total_seconds()
        self.num_rollouts = num_rollouts

    def choose_simulation_node(self):
        """Choose a node from which to simulate a game"""
        node = self.root
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

            if node.N == 0:
                return node

        if self.add_children_to_game_tree(node):
            node = random.choice(node.children)

        return node

    @staticmethod
    def add_children_to_game_tree(parent):
        """
        Create children of parent node, add them to game tree.
        "Expand" in MCTS terminology

        Returns
        -------
            bool: false if the game is over
        """

        if parent.game.winner is not None:
            # don't expand a finished game
            return False

        potential_moves = parent.create_potential_moves(parent)

        child_node_list = []
        for move in potential_moves:
            child_node_list.append(MCTSNode(root_game=move.game, parent=parent))

        parent.children = child_node_list
        return True

    @staticmethod
    def simulate_random_game(simulation_game):
        """
        Find winner of simulated game
        Called 'rollout' in Monte Carlo Tree Search terminology

        This function currently has an awful control structure. Will fix after further testing.
        Attributes
        ----------
        simulation_game : Game object
            starting position of game to simulate

        Returns
        -------
            char : color that won the game
        """
        move_num = 0
        # If no children, the game is done
        while simulation_game.winner is None:
            new_node = MCTSNode(root_game=simulation_game, parent=None)
            potential_node_list = new_node.create_potential_moves(new_node)
            list_len = len(potential_node_list)

            if list_len > 0:
                node_choice = random.choices(population=potential_node_list,
                                             weights=[x.heuristic_score for x in potential_node_list],
                                             k=1)[0]
                simulation_game = node_choice.game
            move_num += 1

        return simulation_game.winner

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
        print(game_choice, "turn:", game_choice.game.turn)
        return game_choice
