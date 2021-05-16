import random
import MCTS
import minimax_node
from math import sqrt

SYS_RANDOM = random.SystemRandom()
SPACE_LIST = [(i, j) for i in range(5) for j in range(5)]
DEPTH = 4
METHOD = 'MINIMAX'

# Todo - add tensorflow reinforcement learning

class Game:
    """
    Implentation of the board game Santorini using Pygame.
    White player chooses actions, while gray turns are automated.
    Attributes
    ----------
    board : list
        5 x 5 board, each space contains level, occupant, and active bool
        active meaning it can be chosen as a space
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
    message : str
        message given to player when they make an invalid choice
        not currently in action on on the pygame board
    """

    def __init__(self):
        self.board = [[{'level': 0, 'occupant': 'O', 'active': False}
                       for i in range(5)] for j in range(5)]
        self.row = 0
        self.col = 0
        self.winner = None
        self.end = False
        self.turn = 0
        self.sub_turn = 'place'
        self.message = ''
        self.color = 'W'

    def __str__(self):
        """
        Create ASCII representation of game state.
        Returns
        -------
        return_val : str
            ASCII represntation of the board
        """
        return_val = "    x0 x1 x2 x3 x4\n"
        return_val += "    --------------\n"
        for i in range(5):
            for j in range(5):
                if j == 0:
                    return_val += 'y' + str(i) + '| '
                return_val += (str(self.board[j][i]['level']) +
                               str(self.board[j][i]['occupant']) +
                               ' ')
            return_val += '\n'
        return return_val[:-1]

    @property
    def dict_key_rep(self):
        """Creates representation of game that can act as key in dictionary"""
        game_str = str(int(self.end)) + str(self.color)
        for i, j in SPACE_LIST:
            game_str += self.board[i][j]['occupant'] + str(self.board[i][j]['level'])
        return game_str

    @property
    def dict_repr(self):
        return {'board':self.board, 'color' : self.color, 'end': self.end}

    @property
    def opponent_color(self):
        return self.get_opponent_color(self.color)

    def get_dict_repr(self, game_dict):
        self.board = game_dict['board']
        self.color = game_dict['color']
        self.end = game_dict['end']
        return self

    def randomize_placement(self, color):
        """Randomly place the two gray pieces on the board."""
        potential_li = []  # list of potential spaces
        all_spaces = [(i, j) for i in range(1, 3, 1) for j in range(1, 3, 1)]

        # For all spaces, get the adjacent space
        for i, j in all_spaces:
            adjacent = get_adjacent(i, j)
            adjacent = filter(lambda x: x[0] in range(1, 3) and x[1] in range(1, 3), adjacent)
            for space in adjacent:
                potential_li.append(((i, j), space))

        # Choose random spaces until we have found one where both
        # spots are open
        chose_spaces = False
        while not chose_spaces:

            # choosing spaces randomly. No function for choosing first space
            space1, space2 = SYS_RANDOM.sample(potential_li, k=1)[0]
            x_0, y_0 = space1
            x_1, y_1 = space2
            if (self.board[x_0][y_0]['occupant'] == 'O' and
                    self.board[x_1][y_1]['occupant'] == 'O'):
                self.board[x_0][y_0]['occupant'] = color
                self.board[x_1][y_1]['occupant'] = color
                chose_spaces = True

    def get_height_score(self, color):
        score = 1
        spaces = [(i, j) for i in range(5) for j in range(5)]
        for i, j in spaces:
            space = self.board[i][j]
            if space['occupant'] == color:
                score += space['level'] ** 2
        return score


    def get_minimax_score(self, color):
        """
        Give numeric score to game.
        Gives a score to the board based on position of the pices
        Used to for the alpha beta pruning algorith
        Parameters
        ----------
        color : char
            Player's perspective from which to evaluate board strenght.
        Returns
        -------
        score : int
            score of the board needed for alpha-beta pruning
            higher score is better
        """
        other_color = self.opponent_color

        score = 0
        spaces = [(i, j) for i in range(5) for j in range(5)]
        for i, j in spaces:
            space = self.board[i][j]
            adjacent_spaces = self.get_movable_spaces(game=self, space=(i, j))

            # 4^level for occupied spaces, 2^level for adjacent spaces
            # in both cases, negative points given for opponent pieces
            if space['occupant'] == color:
                if space['level'] == 3:
                    return 10000
                else:
                    score += 4 ** space['level']
            elif space['occupant'] == other_color:
                if space['level'] == 3:
                    return -10000
                else:
                    score -= 4 ** space['level']

            for k, l in adjacent_spaces:
                space = self.board[k][l]
                if space['occupant'] == color and space['level'] != 4:
                    score += 2 ** space['level']
                elif space['occupant'] == other_color and space['level'] != 4:
                    score -= 2 ** space['level']

        # Loser points for your pieces being far apart, gain for your opponents pieces
        # being far apart
        # todo: have distance score change based on self.turn of turns
        if self.turn < 20:
            score += self.get_distance_score(self.color, other_color) / (self.turn + 1)

        return score

    def undo(self):
        """Undo select action."""
        self.sub_turn = 'select'
        self.make_color_active()

    def make_all_spaces_inactive(self):
        """Get rid of red boxes for all spaces."""
        for i, j in SPACE_LIST:
            self.board[i][j]['active'] = False

    def is_valid_move_space(self, x_val, y_val):
        """
        Check if user made valid movement.
        Parameters
        ----------
        x_val : int
            x coordinate of space
        y_val : int
            y coordinate of space
        Returns
        -------
        bool
            true if move is valid, false if move is invalid
            for a move to be valid, it must be to an unoccupied space and
            no more than one level increase
        """
        height = self.board[x_val][y_val]['level']
        space_list = get_adjacent(x_val, y_val)
        for i, j in space_list:
            if (
                    is_valid_num(i) and is_valid_num(j) and
                    self.board[i][j]['occupant'] == 'O'
                    and self.board[i][j]['level'] - height <= 1
            ):
                return True
        return False

    def is_valid_build_space(self, x_val, y_val):
        """
        Check is user can build on chosen space.
        Parameters
        ----------
        x_val : int
            x coordinate of space
        y_val : int
            y coordinate of space
        Returns
        -------
        bool
            true if player can build there, false otherwise
            player can build on any unoccupied adjacent space
            not that spaces with a dome are considered occupied, with
            an occupant of X
        """
        space_list = get_adjacent(x_val, y_val)
        for i, j in space_list:
            if (is_valid_num(i) and is_valid_num(j) and
                    self.board[i][j]['occupant'] == 'O'):
                return True
        return False

    def end_game(self, switch_color=False):
        """
        End game and prevent further moves.
        Declare the games winner and makes all spaces inactive

        Parameters
        ----------
        switch_color : bool, optional
            switches to opponent before declaring winner
            relevant for secondary win condition (winning through
            opponent having no valid turns). The default is False.
        """
        self.end = True
        if switch_color:
            if self.color == 'W':
                self.color = 'G'
            else:
                self.color = 'W'

        # make all space inactive
        self.make_all_spaces_inactive()
        self.sub_turn = 'end'

    def make_color_active(self):
        """
        Mark pieces as active.
        For a given player color, mark all the spaces with that
        player color as active
        """

        # Check if spaces match color and worker can move
        for i, j in SPACE_LIST:
            self.board[i][j]['active'] = (self.board[i][j]['occupant'] == self.color and
                                          len(self.get_movable_spaces(self, (i, j), False)) > 0)

    def make_choice_active(self, x_val, y_val):
        """
        Mark the piece a player has chosen as active.
        Parameters
        ----------
        x_val : int
            x coordinate of chosen piece
        y_val : int
            y coordinate of chosen piece
        """
        for j, i in SPACE_LIST:
            self.board[i][j]['active'] = \
                i == x_val and j == y_val

    def highlight_movable_spaces(self):
        """
        Mark build-able spaces.
        after a player moves, marks the surrounding pieces
        where they can build as active
        """
        # Check if each space represents a valid place to build
        for j in range(5):
            for i in range(5):
                self.board[i][j]['active'] = \
                    abs(i - self.col) <= 1 and \
                    abs(j - self.row) <= 1 and \
                    not (i == self.col and j == self.row) and \
                    self.board[i][j]['occupant'] == 'O'

    def check_move_available(self):
        """End game if player has no available moves."""
        for j, i in SPACE_LIST:
            if (self.board[i][j]['occupant'] == self.color and
                    self.is_valid_move_space(i, j)):
                return  # end function if we have a valid space
        self.end_game(True)

    def check_build_available(self):
        """End game if player has no available builds."""
        for j, i in SPACE_LIST:
            if (
                    self.board[i][j]['occupant'] == self.color and
                    self.is_valid_build_space(i, j)):
                return  # end function if we have a valid space
        self.end_game(True)

    def place_worker(self, color, x_val, y_val):  # Only runs at beginning of game
        """
        Place two pieces of given color on the board.
        Parameters
        ----------
        color : str
            player color that will be placed on the board
        """
        if self.board[x_val][y_val]['occupant'] != 'O':
            self.message = "Occupied Space"
        else:
            self.board[x_val][y_val]['occupant'] = color
            return True
        return False

    def select_worker(self, color, x_val, y_val):
        """
        Choose piece to move.
        Parameters
        ----------
        color : str
            Color of current player
        x_val : int
            x coordinate of spot on board
        y_val : int
            y coordinate of spont on board
        Returns
        -------
        bool
            True/false if move is valid
        """
        if self.board[x_val][y_val]['occupant'] != color:
            self.message = "You don't own that piece"
        else:
            self.col = x_val
            self.row = y_val
            self.make_choice_active(x_val, y_val)
            self.sub_turn = 'move'
            return True
        return False

    def move_worker(self, x_val, y_val, auto=False):
        """
        Move piece to new spot on board.
        Parameters
        ----------
        x_val : int
            x-coordinate
        y_val : int
            y-coordinate
        Returns
        -------
        bool
            True if move is valid
        """
        prev_col = self.col  # x
        prev_row = self.row  # y
        if not auto and (abs(y_val - prev_row) > 1 or
                         abs(x_val - prev_col) > 1) or \
                y_val == prev_row and x_val == prev_col or \
                self.board[x_val][y_val]['occupant'] != 'O' or \
                (self.board[x_val][y_val]['level'] -
                 self.board[prev_col][prev_row]['level'] > 1):
            return False
        else:
            self.board[x_val][y_val]['occupant'] = self.color
            self.board[prev_col][prev_row]['occupant'] = 'O'
            if self.board[x_val][y_val]['level'] == 3:
                self.end_game()
            self.col = x_val
            self.row = y_val
            self.sub_turn = 'build'
            self.highlight_movable_spaces()
            return True

    def build_level(self, x_val, y_val, auto=False):
        """
        Build on a space.
        Parameters
        ----------
        x_val : int
            x coordinate
        y_val : int
            y coordinate
        Returns
        -------
        bool
            True if move is valid
        """
        if not auto and (abs(y_val - self.row) > 1 or
                         abs(x_val - self.col) > 1) or \
                y_val == self.row and x_val == self.col or \
                self.board[x_val][y_val]['occupant'] != 'O':
            return False
        else:
            self.board[x_val][y_val]['level'] += 1
            if self.board[x_val][y_val]['level'] == 4:
                self.board[x_val][y_val]['occupant'] = 'X'
            self.sub_turn = 'switch'
            self.turn += 1
            return True

    def play_manual_turn(self, x_val, y_val):
        """
        Run through a turn.
        After the piece placement has taken place, goes through
        motion of a normal turn.
        Parameters
        ----------
        x_val : int
            x coordinate
        y_val : int
            y coordinate
        """
        # Playing the regular game
        if self.sub_turn == 'select':  # Selecting which piece to move
            self.make_color_active()
            self.select_worker(self.color, x_val, y_val)
        elif self.sub_turn == 'move':  # Moving that piece
            self.check_move_available()
            self.move_worker(x_val, y_val)
        elif self.sub_turn == 'build':
            self.build_level(x_val, y_val)

    def play_minimax_turn(self, move_color, eval_color=None, tree_depth=DEPTH):
        """
        Select turn for AI player
        Uses alpha-beta pruning to selection best turn
        and update game object to that ideal turn
        Parameters
        ----------
        move_color : char
            Whose turn is it is. This will be the color moved
        eval_color : char
            Color to use for the eval function. Which perpective to score from
        tree_depth : int
            Depth of the tree. How far to look ahead for creating potential moves
        """
        if self.end:
            return

        game_copy = self.game_deep_copy(self, self.color)
        root_node = minimax_node.MiniMaxNode(game=game_copy,
                                             children=[])
        best_state = root_node.alpha_beta_move_selection(root_node=root_node, depth=tree_depth,
                                                         move_color=move_color, eval_color=eval_color)[1]
        if best_state is None:
            best_state = root_node.create_potential_moves(node=root_node, eval_color=eval_color, move_color=move_color)[
                0]
        self.board = best_state.game.board
        self.end = best_state.game.end

        if not self.end:
            self.sub_turn = 'switch'

    def play_mcts_turn(self, move_color):
        """
        Select turn for AI player
        Uses alpha-beta pruning to selection best turn
        and update game object to that ideal turn
        Parameters
        ----------
        move_color : char
            Whose turn is it is. This will be the color moved
        """
        self.color = move_color
        self.check_move_available()
        if self.end:
            return

        game_copy = self.game_deep_copy(self, move_color)
        mcts_game_tree = MCTS.TreeSearch(game_copy)
        mcts_game_tree.search_tree()
        best_node = mcts_game_tree.get_best_move()
        self.board = best_node.game.board
        self.end = best_node.game.end
        self.turn = best_node.game.turn
        self.winner = best_node.game.winner

        if not self.end:
            self.sub_turn = 'switch'

    def get_distance_score(self, color, opponent_color):
        player_spaces = []
        opponent_spaces = []
        for col, row in [(i, j) for i in range(5) for j in range(5)]:
            if self.board[col][row]['occupant'] == color:
                player_spaces.append((col, row))
            elif self.board[col][row]['occupant'] == opponent_color:
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
            if self.board[i][j]['level'] == 3 and self.board[i][j]['occupant'] == move_color:
                self.end = True
                return True

        return False

    @staticmethod
    def game_deep_copy(game, color):
        """
        Deep copies board from another game.
        Used as part of the create children functions. Standard
        Python copy.deepcopy was too slow.
        Parameters
        ----------
        game : Game
            game from which to copy info
        color :
            color to set as the player of that game
        Returns
        -------
        new_game : Game
            new game with same info as others and a new color
        """
        new_game = Game()
        other_board = game.board

        new_board = [[{'level': 0, 'occupant': 'O', 'active': False}
                      for i in range(5)] for j in range(5)]

        for i, j in SPACE_LIST:
            new_board[i][j]['occupant'] = other_board[i][j]['occupant']
            new_board[i][j]['level'] = other_board[i][j]['level']

        new_game.board = new_board
        new_game.end = game.end
        new_game.col = game.col
        new_game.row = game.row
        new_game.color = color
        new_game.turn = game.turn

        return new_game

    @staticmethod
    def get_movable_spaces(game, space, return_iter=True):
        return_li = []
        x_val, y_val = space
        height = game.board[x_val][y_val]['level']
        for spot in get_adjacent(x_val, y_val):
            x_adj, y_adj = spot
            if (game.board[x_adj][y_adj]['occupant'] == 'O' and
                    (game.board[x_adj][y_adj]['level'] - height) <= 1):
                return_li.append((x_adj, y_adj))

        # Choose to return either iterator or list
        if return_iter:
            return iter(return_li)
        else:
            return return_li

    @staticmethod
    def get_buildable_spaces(game, space):
        return_li = []
        x_val, y_val = space
        for spot in get_adjacent(x_val, y_val):
            x_adj, y_adj = spot
            if (game.board[x_adj][y_adj]['occupant'] == 'O'):
                return_li.append((x_adj, y_adj))

        return iter(return_li)

    @staticmethod
    def get_opponent_color(color):
        """Get player color that isn't the one passed

        Parameters
        ----------
        color : char
            Either W or G. Color of the current player

        """
        if color == 'W':
            other_color = 'G'
        else:
            other_color = 'W'
        return other_color

    def game_has_cap(self):
        for i, j in SPACE_LIST:
            if self.board[i][j]['level'] == 4:
                return True
        return False


def get_adjacent(x_val, y_val):
    """
    Get spaces surrounding the passed one.
    Parameters
    ----------
    x_val : int
        x_valdinate ie column value
    y_val : int
        y_valdinate ie row value
    when : string
        Not currently used. Idea is to use function to get adjacent
        values base on phase of the game. eg account for height during build
        phase
    Returns
    -------
    space_li : li
        list of spaces adjacent to the one provided through
        x_val and y_val
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
    Parameters
    ----------
    num : str
        row or column value
    Returns
    -------
    bool
        true if its a valid number [0,4]
        false otherwise
    """
    return -1 < num < 5

def distance_between(col_0, row_0, col_1, row_1):
    return sqrt((col_0 - col_1) ** 2 + (row_0 - row_1) ** 2)
