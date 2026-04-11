import random
import MCTS
import MCTS_RAVE
import minimax_node
from math import sqrt

SYS_RANDOM = random.SystemRandom()
SPACE_LIST = [(i, j) for i in range(5) for j in range(5)]

# Precomputed adjacency list for all 25 squares — avoids recomputing on every call
ADJACENT = {
    (i, j): [(i+di, j+dj)
              for di in (-1, 0, 1) for dj in (-1, 0, 1)
              if (di != 0 or dj != 0) and 0 <= i+di <= 4 and 0 <= j+dj <= 4]
    for i in range(5) for j in range(5)
}

class Game:
    """
    Implementation of the board game Santorini using Pygame.

    Attributes
    ----------
    levels : list
        Flat list of 25 ints representing building levels. Access via levels[i*5+j]
    occupants : list
        Flat list of 25 strings representing piece occupants ('O', 'W', 'G', 'X'). Access via occupants[i*5+j]
    actives : list
        Flat list of 25 bools for GUI highlighting. Access via actives[i*5+j]
    row : int
        current row chosen by player
    col : int
        current column chosen by player
    end : bool
        true if game has ended
    color : char
        player color, G(ray) or W(hite)
    turn : int
        which turn the game is on
    sub_turn : str
        action within a turn: place, select, move, or build
    """

    def __init__(self):
        self.levels = [0] * 25
        self.occupants = ['O'] * 25
        self.actives = [False] * 25
        self.row = 0
        self.col = 0
        self.winner = None
        self.prev_game = None  # snapshot for undo
        self.end = False
        self.turn = 0
        self.sub_turn = 'place'
        self.color = 'W'

    def __str__(self):
        """
        Create ASCII representation of game state.
        Returns
        -------
        return_val : str
            ASCII representation of the board
        """
        return_val = "    x0 x1 x2 x3 x4\n"
        return_val += "    --------------\n"
        for i in range(5):
            for j in range(5):
                if j == 0:
                    return_val += 'y' + str(i) + '| '
                return_val += (str(self.levels[j*5+i]) +
                               str(self.occupants[j*5+i]) +
                               ' ')
            return_val += '\n'
        return return_val[:-1]

    @property
    def board(self):
        """Build 2D dict board for GUI compatibility. Not used in hot path."""
        return [[{'level': self.levels[i*5+j],
                  'occupant': self.occupants[i*5+j],
                  'active': self.actives[i*5+j]}
                 for j in range(5)] for i in range(5)]

    @property
    def opponent_color(self):
        return self.get_opponent_color(self.color)

    def randomize_placement(self, color):
        """Randomly place the two pieces of given color on the board."""
        potential_li = []
        all_spaces = [(i, j) for i in range(1, 3, 1) for j in range(1, 3, 1)]

        for i, j in all_spaces:
            adjacent = get_adjacent(i, j)
            adjacent = filter(lambda x: x[0] in range(1, 3) and x[1] in range(1, 3), adjacent)
            for space in adjacent:
                potential_li.append(((i, j), space))

        chose_spaces = False
        while not chose_spaces:
            space1, space2 = SYS_RANDOM.sample(potential_li, k=1)[0]
            x_0, y_0 = space1
            x_1, y_1 = space2
            if (self.occupants[x_0*5+y_0] == 'O' and
                    self.occupants[x_1*5+y_1] == 'O'):
                self.occupants[x_0*5+y_0] = color
                self.occupants[x_1*5+y_1] = color
                chose_spaces = True

    def get_height_score(self, color):
        score = 0
        for i, j in SPACE_LIST:
            idx = i*5+j
            if self.occupants[idx] == color:
                score += 2 * self.levels[idx] + 1
        return score

    def get_minimax_score(self, color):
        """
        Give numeric score to game.
        Parameters
        ----------
        color : char
            Player's perspective from which to evaluate board strength.
        Returns
        -------
        score : int
            score of the board needed for alpha-beta pruning
        """
        other_color = self.opponent_color
        score = 0
        for i, j in SPACE_LIST:
            idx = i*5+j
            occ = self.occupants[idx]
            lvl = self.levels[idx]
            adjacent_spaces = self.get_movable_spaces(game=self, space=(i, j))

            if occ == color:
                if lvl == 3:
                    return 10000
                else:
                    score += 4 ** lvl
            elif occ == other_color:
                if lvl == 3:
                    return -10000
                else:
                    score -= 4 ** lvl

            for k, l in adjacent_spaces:
                kidx = k*5+l
                kocc = self.occupants[kidx]
                klvl = self.levels[kidx]
                if kocc == color and klvl != 4:
                    score += 2 ** klvl
                elif kocc == other_color and klvl != 4:
                    score -= 2 ** klvl

        if self.turn < 20:
            score += self.get_distance_score(self.color, other_color) / (self.turn + 1)

        return score

    def undo(self):
        """Restore game to snapshot taken before last move or build."""
        if self.prev_game is not None:
            self.levels = self.prev_game.levels[:]
            self.occupants = self.prev_game.occupants[:]
            self.turn = self.prev_game.turn
            self.end = self.prev_game.end
            self.winner = self.prev_game.winner
            self.col = self.prev_game.col
            self.row = self.prev_game.row
            self.prev_game = None
            # Always return to select phase and re-highlight active workers
            self.sub_turn = 'select'
            self.make_color_active()

    def highlight_placement_spaces(self):
        """Highlight all empty spaces during piece placement."""
        for i, j in SPACE_LIST:
            self.actives[i*5+j] = (self.occupants[i*5+j] == 'O')

    def make_all_spaces_inactive(self):
        """Get rid of red boxes for all spaces."""
        self.actives = [False] * 25

    def is_valid_move_space(self, x_val, y_val):
        """
        Check if user made valid movement.
        Returns
        -------
        bool
            true if move is valid, false if move is invalid
        """
        height = self.levels[x_val*5+y_val]
        for i, j in ADJACENT[(x_val, y_val)]:
            if (self.occupants[i*5+j] == 'O' and
                    self.levels[i*5+j] - height <= 1):
                return True
        return False

    def is_valid_build_space(self, x_val, y_val):
        """
        Check if user can build on chosen space.
        Returns
        -------
        bool
            true if player can build there, false otherwise
        """
        for i, j in ADJACENT[(x_val, y_val)]:
            if self.occupants[i*5+j] == 'O':
                return True
        return False

    def end_game(self, switch_color=False):
        """
        End game and prevent further moves.
        Parameters
        ----------
        switch_color : bool, optional
            switches to opponent before declaring winner
        """
        self.end = True
        if switch_color:
            if self.color == 'W':
                self.color = 'G'
            else:
                self.color = 'W'
        self.make_all_spaces_inactive()
        self.sub_turn = 'end'

    def make_color_active(self):
        """Mark pieces as active for a given player color."""
        for i, j in SPACE_LIST:
            idx = i*5+j
            self.actives[idx] = (self.occupants[idx] == self.color and
                                  len(self.get_movable_spaces(self, (i, j), False)) > 0)

    def make_choice_active(self, x_val, y_val):
        """Mark the piece a player has chosen as active."""
        for j, i in SPACE_LIST:
            self.actives[i*5+j] = (i == x_val and j == y_val)

    def highlight_movable_spaces(self):
        """Mark buildable spaces after a player moves."""
        self.actives = [False] * 25
        for i, j in ADJACENT[(self.col, self.row)]:
            if self.occupants[i*5+j] == 'O':
                self.actives[i*5+j] = True

    def check_move_available(self):
        """End game if player has no available moves."""
        for j, i in SPACE_LIST:
            if (self.occupants[i*5+j] == self.color and
                    self.is_valid_move_space(i, j)):
                return
        self.end_game(True)

    def check_build_available(self):
        """End game if player has no available builds."""
        for j, i in SPACE_LIST:
            if (self.occupants[i*5+j] == self.color and
                    self.is_valid_build_space(i, j)):
                return
        self.end_game(True)

    def place_worker(self, color, x_val, y_val):
        """Place piece of given color on the board."""
        idx = x_val*5+y_val
        if self.occupants[idx] != 'O':
            pass
        else:
            self.occupants[idx] = color
            return True
        return False

    def select_worker(self, color, x_val, y_val):
        """Choose piece to move."""
        if self.occupants[x_val*5+y_val] != color:
            pass
        else:
            self.col = x_val
            self.row = y_val
            self.make_choice_active(x_val, y_val)
            self.sub_turn = 'move'
            return True
        return False

    def move_worker(self, x_val, y_val, auto=False):
        """Move piece to new spot on board."""
        if not auto:
            self.prev_game = self.game_deep_copy(self, self.color)
        prev_col = self.col
        prev_row = self.row
        if not auto and (abs(y_val - prev_row) > 1 or
                         abs(x_val - prev_col) > 1) or \
                y_val == prev_row and x_val == prev_col or \
                self.occupants[x_val*5+y_val] != 'O' or \
                (self.levels[x_val*5+y_val] -
                 self.levels[prev_col*5+prev_row] > 1):
            return False
        else:
            self.occupants[x_val*5+y_val] = self.color
            self.occupants[prev_col*5+prev_row] = 'O'
            if self.levels[x_val*5+y_val] == 3:
                self.end_game()
            self.col = x_val
            self.row = y_val
            self.sub_turn = 'build'
            self.highlight_movable_spaces()
            return True

    def build_level(self, x_val, y_val, auto=False):
        """Build on a space."""
        if not auto:
            self.prev_game = self.game_deep_copy(self, self.color)
        idx = x_val*5+y_val
        if not auto and (abs(y_val - self.row) > 1 or
                         abs(x_val - self.col) > 1) or \
                y_val == self.row and x_val == self.col or \
                self.occupants[idx] != 'O':
            return False
        else:
            self.levels[idx] += 1
            if self.levels[idx] == 4:
                self.occupants[idx] = 'X'
            self.sub_turn = 'switch'
            self.turn += 1
            return True

    def play_manual_turn(self, x_val, y_val):
        """Run through a human turn."""
        if self.sub_turn == 'place':
            if self.place_worker(self.color, x_val, y_val):
                self.highlight_placement_spaces()
        elif self.sub_turn == 'select':
            self.make_color_active()
            self.select_worker(self.color, x_val, y_val)
        elif self.sub_turn == 'move':
            self.check_move_available()
            self.move_worker(x_val, y_val)
        elif self.sub_turn == 'build':
            self.build_level(x_val, y_val)

    def play_minimax_turn(self, move_color, eval_color=None, tree_depth=4):
        """Select turn for minimax AI player using alpha-beta pruning."""
        if self.end:
            return

        game_copy = self.game_deep_copy(self, self.color)
        root_node = minimax_node.MiniMaxNode(game=game_copy, children=[])
        best_state = root_node.alpha_beta_move_selection(root_node=root_node, depth=tree_depth,
                                                         move_color=move_color, eval_color=eval_color)[1]
        if best_state is None:
            best_state = root_node.create_potential_moves(node=root_node, eval_color=eval_color, move_color=move_color)[0]

        self.levels = best_state.game.levels[:]
        self.occupants = best_state.game.occupants[:]
        self.actives = best_state.game.actives[:]
        self.end = best_state.game.end

        if not self.end:
            self.sub_turn = 'switch'

    def play_mcts_turn(self, move_color, rave=True):
        """Select turn for MCTS AI player."""
        self.check_move_available()
        if self.end:
            return

        game_copy = self.game_deep_copy(self, move_color)
        if not rave:
            mcts_game_tree = MCTS.TreeSearch(game_copy)
        elif rave:
            mcts_game_tree = MCTS_RAVE.TreeSearchRave(game_copy)
        mcts_game_tree.search_tree()
        best_node = mcts_game_tree.get_best_move()
        self.levels = best_node.game.levels[:]
        self.occupants = best_node.game.occupants[:]
        self.actives = best_node.game.actives[:]
        self.end = best_node.game.end
        self.turn = best_node.game.turn
        self.winner = best_node.game.winner

        if not self.end:
            self.sub_turn = 'switch'

    def get_distance_score(self, color, opponent_color):
        player_spaces = []
        opponent_spaces = []
        for col, row in SPACE_LIST:
            occ = self.occupants[col*5+row]
            if occ == color:
                player_spaces.append((col, row))
            elif occ == opponent_color:
                opponent_spaces.append((col, row))

        player_col_0, player_row_0 = player_spaces[0]
        player_col_1, player_row_1 = player_spaces[1]
        opponent_col_0, opponent_row_0 = opponent_spaces[0]
        opponent_col_1, opponent_row_1 = opponent_spaces[1]

        return -1 * (distance_between(player_col_0, player_row_0, opponent_col_0, opponent_row_0) +
                     distance_between(player_col_0, player_row_0, opponent_col_1, opponent_row_1) +
                     distance_between(player_col_1, player_row_1, opponent_col_1, opponent_row_1) +
                     distance_between(player_col_1, player_row_1, opponent_col_0, opponent_row_0))

    def is_winning_move(self, move_color=None):
        if move_color is None:
            move_color = self.color

        for i, j in SPACE_LIST:
            idx = i*5+j
            if self.levels[idx] == 3 and self.occupants[idx] == move_color:
                self.end = True
                return True

        return False

    @staticmethod
    def game_deep_copy(game, color):
        """
        Deep copies game state.
        Uses flat list slices for maximum copy speed.
        Parameters
        ----------
        game : Game
            game from which to copy info
        color :
            color to set as the player of that game
        Returns
        -------
        new_game : Game
            new game with same info as original
        """
        new_game = object.__new__(Game)
        new_game.levels = game.levels[:]
        new_game.occupants = game.occupants[:]
        new_game.actives = [False] * 25
        new_game.end = game.end
        new_game.winner = game.winner
        new_game.col = game.col
        new_game.row = game.row
        new_game.color = color
        new_game.turn = game.turn
        new_game.sub_turn = game.sub_turn
        return new_game

    @staticmethod
    def get_movable_spaces(game, space, return_iter=True):
        return_li = []
        x_val, y_val = space
        height = game.levels[x_val*5+y_val]
        for x_adj, y_adj in ADJACENT[(x_val, y_val)]:
            idx = x_adj*5+y_adj
            if (game.occupants[idx] == 'O' and
                    (game.levels[idx] - height) <= 1):
                return_li.append((x_adj, y_adj))
        if return_iter:
            return iter(return_li)
        else:
            return return_li

    @staticmethod
    def get_buildable_spaces(game, space):
        return_li = []
        x_val, y_val = space
        for x_adj, y_adj in ADJACENT[(x_val, y_val)]:
            if game.occupants[x_adj*5+y_adj] == 'O':
                return_li.append((x_adj, y_adj))
        return iter(return_li)

    @staticmethod
    def get_opponent_color(color):
        """Get player color that isn't the one passed."""
        if color == 'W':
            return 'G'
        return 'W'


def get_adjacent(x_val, y_val):
    """
    Get spaces surrounding the passed one.
    Parameters
    ----------
    x_val : int
        x_coordinate ie column value
    y_val : int
        y_coordinate ie row value
    Returns
    -------
    space_li : list
        list of spaces adjacent to the one provided
    """
    space_list = [(x_val - 1, y_val + 1),
                  (x_val, y_val + 1),
                  (x_val + 1, y_val + 1),
                  (x_val - 1, y_val),
                  (x_val + 1, y_val),
                  (x_val - 1, y_val - 1),
                  (x_val, y_val - 1),
                  (x_val + 1, y_val - 1)]
    space_list = iter(list(filter(
        lambda t: t[0] >= 0 and t[0] <= 4
                  and t[1] >= 0 and t[1] <= 4,
        space_list)))

    return space_list


def is_valid_num(num):
    """
    Check if x or y falls on board.
    Returns
    -------
    bool
        true if its a valid number [0,4]
    """
    return -1 < num < 5


def distance_between(col_0, row_0, col_1, row_1):
    """Geometric distance between two points"""
    return sqrt((col_0 - col_1) ** 2 + (row_0 - row_1) ** 2)
