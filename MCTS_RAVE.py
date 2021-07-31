"""Simplified addition of the All Moves as First (AMAF) algorithm to MCTS"""

import random
from math import sqrt, log

from MCTS import MCTSNode, TreeSearch

EXPLORATION_FACTOR_RAVE = 2.5  # Parameter that decides tradeoff between exploration and exploitation
RAVE_EQUILIBRIUM = 50  # Number of moves after which RAVE and MCTS have equal value


class RAVENode(MCTSNode):

    def __init__(self, root_game, parent, simulation_exception=None, rave_id=0):
        super().__init__(root_game, parent, simulation_exception)
        self.RAVE_N = 0
        self.RAVE_Q = 0
        self.RAVE_id = rave_id

    def __repr__(self):
        """ASCII representation of MCTS Node."""
        if self.N == 0 or self.parent is None:
            return str(self.game) + self.game.color

        return (str(self.game) + self.game.color + '\n'
                + str(self.Q) + '/' + str(self.N)
                + ': ' + str(round(100 * self.Q / self.N, 1)) + '%'
                + ' (' + str(self.RAVE_Q) + '/' + str(self.RAVE_N) + ')'
                + ' score: ' + str(round(self.mcts_score, 3)))

    @staticmethod
    def create_potential_moves(node):
        """
        Add list of possible moves to game state.

        Parameters
        ----------
        node : RAVENode
            Parent node of all potential moves
        Returns
        -------
        return_li : list
            Children of that node
        """
        rave_id = -1  # initialize rave id
        potential_move_li = []  # list of legal moves from current game state
        simulation_exception = None  # extra weight to put on simulation score

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

        winning_move = node.find_losing_spaces(other_color)

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
                    potential_move_li = [RAVENode(root_game=new_game, parent=node)]
                    return potential_move_li
                else:
                    # given a legal move, check for each possible build
                    rave_id += 1
                    for build in new_game.get_buildable_spaces(new_game, (new_game.col, new_game.row)):

                        if build == winning_move:
                            simulation_exception = 'block_win'  # block opponent from winning
                        elif (new_game.board[new_game.col][new_game.row]['level'] == 2 and
                              new_game.board[build[0]][build[1]]['level'] == 3):
                            simulation_exception = 'create_win'  # create winning move
                        build_game = new_game.game_deep_copy(new_game,
                                                             new_game.color)
                        build_game.build_level(build[0], build[1], auto=True)
                        potential_move_li.append(RAVENode(root_game=build_game,
                                                          parent=node,
                                                          simulation_exception=simulation_exception,
                                                          rave_id=rave_id))

        # If no move can be made, player loses
        if len(potential_move_li) == 0:
            node.game.winner = other_color

        return potential_move_li

    @property
    def mcts_score(self, exploration_factor=EXPLORATION_FACTOR_RAVE, rave_equilibrium=RAVE_EQUILIBRIUM):
        """Upper confidence bound for this node

        Attributes
        ----------
        exploration_factor : float
            Tradeoff between exploring new nodes and exploring those with high win rates
        """

        # Set exploration factor, want to exploit less earlier in the game
        if self.game.turn > 16:
            exploration_factor = EXPLORATION_FACTOR_RAVE * 0.50
        elif self.game.turn > 8:
            exploration_factor = EXPLORATION_FACTOR_RAVE * 0.75

        if self.N == 0:  # what to do if node hasn't been visited
            self.early_game_score = self.establish_model_score()
            return float('inf')
        else:
            rave_weight = sqrt(RAVE_EQUILIBRIUM / (3 * self.parent.N + RAVE_EQUILIBRIUM))
            mcts_weight = (1 - rave_weight)

            # (win_rate) + (constant * heuristic_score * exploitation)
            return ((self.Q / self.N) * mcts_weight + (self.RAVE_Q / self.RAVE_N) * rave_weight
                    + self.early_game_score * exploration_factor * sqrt(log(self.parent.N) / self.N))


class TreeSearchRave(TreeSearch):

    def __init__(self, root_game):
        super().__init__(root_game)
        self.root = RAVENode(self.root_game, None)

    @staticmethod
    def update_node_info(node, outcome):
        """
        Update the node and its parents with its winning percentage.

        Attributes
        ----------
        node : MCTSNode
            Node from which simulation was run

        outcome : char
            W or G, winner of the simulation game
        """
        reward = int(outcome == node.game.color)

        while node is not None:
            node.N += 1
            node.Q += reward

            # See if child node has siblings to loop through
            if node.parent is None:
                siblings = []
            else:
                siblings = node.parent.children

            for child in siblings:
                if child.RAVE_id == node.RAVE_id:
                    child.RAVE_N += 1
                    child.RAVE_Q += reward

            node = node.parent  # traverse up the tree
            reward = int(not reward)  # switch reward for other color

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

        parent.children = parent.create_potential_moves(parent)
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
            new_node = RAVENode(root_game=simulation_game, parent=None)
            potential_node_list = new_node.create_potential_moves(new_node)
            list_len = len(potential_node_list)

            if list_len > 0:
                node_choice = random.choices(population=potential_node_list,
                                             weights=[x.simulation_score for x in potential_node_list],
                                             k=1)[0]
                simulation_game = node_choice.game

        return simulation_game.winner

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
