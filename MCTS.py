"""
Implementation of Monte Carlo Tree Search. Currently working on improving early game moves.
"""

import datetime as dt
import random
from math import sqrt, log, exp

EXPLORATION_FACTOR = sqrt(2)  # Parameter that decides tradeoff between exploration and exploitation
TURN_TIME = 75  # Max amount of time MCTS agent can search for best move
MAX_ROLLOUT = 15000  # Max number of rollouts MCTS agent can have before choosing best move
SPACE_LIST = [(i, j) for i in range(5) for j in range(5)]  # List of spaces in board, used with for loops

random.seed(dt.datetime.now().microsecond)  # set seed


class MCTSNode:
    """
    Node used to create game tree for MCTS.

    Attributes
    ----------
    game : Game
        Santorini game of this node
    parent : MCTSNode
       Parent node, ie previous game state
    children : list
        Legal moves following this node. Empty if game is over.
    N : int
        # of times node has been visited in a search
    Q : int
        # of times node has won when simulated
    deleted : bool
        Not currently in use, could be used to prune trees in the future
    """

    def __init__(self, root_game, parent, winning_cap=False):

        self.game = root_game
        self.parent = parent
        self.children = []
        self.N = 0
        self.Q = 0
        self.deleted = False
        self.early_game_score = 0
        self.winning_cap = winning_cap

    def __repr__(self):
        """ASCII representation of MCTS Node."""
        if self.N == 0 or self.parent is None:
            return str(self.game) + self.game.color

        return (str(self.game) + self.game.color + '\n' + str(self.Q) + '/' + str(self.N) + ' '
                + str(round(100 * self.Q / self.N, 1)) +
                '%, score: ' + str(round(self.mcts_score, 6)))

    def cap_opponent_win(self, other_color):
        win_space = (-1, -1)  # default if no space is found

        i = 0  # column value in outer loop
        j = 0  # row value in outer loop
        found_space = False

        while not found_space and i <= 4 and j <= 4:
            if self.game.board[i][j]['occupant'] == other_color and self.game.board[i][j]['level'] == 2:
                for col, row in self.game.get_movable_spaces(game=self.game, space=(i, j)):
                    if self.game.board[col][row]['level'] == 3:
                        win_space = (col, row)
                        found_space = True
            # iterate to next column. If we finish a column, go to next row
            i += 1
            if i == 5:
                i = 0
                j += 1

        # only worth checking for blocked moves if only once space exists
        # If none, we can ignore. If multiple, we can't block it anyway
        return win_space

    def establish_early_game_score(self):
        """Heuristic score used to prune first 8 moves of MCTS agent's turn."""
        this_game = self.game
        if this_game.turn > 20:
            return 1

        color = this_game.color
        player_height_score = 0  # to make height score somewhat match the height score property
        opponent_color = this_game.opponent_color
        opponent_height = 1
        player_spaces = []
        opponent_spaces = []
        for col, row in [(i, j) for i in range(5) for j in range(5)]:
            if this_game.board[col][row]['occupant'] == color:
                player_height_score += 2 ** this_game.board[col][row]['level']
                player_spaces.append((col, row))
            elif this_game.board[col][row]['occupant'] == opponent_color:
                opponent_height += this_game.board[col][row]['level']
                for col_, row_ in this_game.get_movable_spaces(game=this_game, space=(col, row)):
                    player_height_score -= this_game.board[col_][row_]['level'] // 2
                opponent_spaces.append((col, row))

        player_col_0, player_row_0 = player_spaces[0]
        player_col_1, player_row_1 = player_spaces[1]

        opponent_col_0, opponent_row_0 = opponent_spaces[0]
        opponent_col_1, opponent_row_1 = opponent_spaces[1]

        distance_score = -1 * opponent_height // 2 * (
                distance_between(player_col_0, player_row_0, opponent_col_0, opponent_row_0) +
                distance_between(player_col_0, player_row_0, opponent_col_1, opponent_row_1) +
                distance_between(player_col_1, player_row_1, opponent_col_1, opponent_row_1) +
                distance_between(player_col_1, player_row_1, opponent_col_0, opponent_row_0))

        # Arithmetic mean of distance and height score
        # 8 being the maximum height score
        score = distance_score / sqrt(32) + player_height_score
        transform_score = 1 / (1 + exp(score * -1))
        return transform_score

    @property
    def height_score(self):
        """Height (aka level) of player pieces."""
        if not self.winning_cap:
            return self.game.get_height_score(self.game.color)
        else:
            return 200

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
            other_color = 'G'
        else:
            move_color = 'G'
            other_color = 'W'

        winning_move = node.cap_opponent_win(other_color)

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
                    new_game.winner = move_color
                    potential_move_li = [MCTSNode(root_game=new_game, parent=node)]
                    return potential_move_li
                else:
                    # given a legal move, check for each possible build
                    for build in new_game.get_buildable_spaces(new_game, (new_game.col, new_game.row)):

                        build_game = new_game.game_deep_copy(new_game,
                                                             new_game.color)

                        build_game.build_level(build[0], build[1], auto=True)
                        potential_move_li.append(MCTSNode(root_game=build_game,
                                                          parent=node,
                                                          winning_cap=build == winning_move))

        if len(potential_move_li) == 0:
            node.game.winner = other_color

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
            self.early_game_score = self.establish_early_game_score()
            return float('inf')
        else:
            # Exploration (win rate) + exploitation + heuristic
            return (self.Q / self.N
                    + self.early_game_score * exploration_factor * sqrt(log(self.parent.N) / self.N))


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
        while num_rollouts < MAX_ROLLOUT and (current_time - start_time).total_seconds() < max_seconds:
            node = self.choose_simulation_node()
            simulation_game = node.game.game_deep_copy(node.game, node.game.color)
            winning_color = self.simulate_random_game(simulation_game)
            self.update_node_info(node, winning_color)
            num_rollouts += 1
            current_time = dt.datetime.now()
        print("rollouts:", num_rollouts)
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
            node = random.choices(population=max_child_list,
                                  weights=[x.height_score for x in max_child_list],
                                  k=1)[0]
            # node = random.choice(max_child_list)
            if node.N == 0:
                return node

        if self.add_children_to_game_tree(node):
            if len(node.children) > 0:
                node = random.choice(node.children)
            else:
                print("exception")
                print(node, node.game.winner, node.game.turn)

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

        # If no children, the game is done
        while simulation_game.winner is None:
            new_node = MCTSNode(root_game=simulation_game, parent=None)
            potential_node_list = new_node.create_potential_moves(new_node)
            list_len = len(potential_node_list)

            if list_len > 0:
                node_choice = random.choices(population=potential_node_list,
                                             weights=[x.height_score for x in potential_node_list],
                                             k=1)[0]
                simulation_game = node_choice.game

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
        print(game_choice, "turn:", game_choice.parent.game.turn)
        return game_choice


def distance_between(col_0, row_0, col_1, row_1):
    """Geometrics distance between two points"""
    return sqrt((col_0 - col_1) ** 2 + (row_0 - row_1) ** 2)
