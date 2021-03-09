# pylint: disable=E0633
import datetime as dt
import random
from copy import deepcopy

from node import Node, store_breadth_first

SYS_RANDOM = random.SystemRandom()
SPACE_LIST = [(i, j) for i in range(5) for j in range(5)]
DEPTH = 4
PICKLE = False


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
        self.end = False
        self.turn = 1
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
        return_val = ''  # 'score: ' + str(self.evaluate_board()) + ' \n'
        return_val += "    x0 x1 x2 x3 x4\n"
        return_val += "    --------------\n"
        for i in range(5):
            for j in range(5):
                if j == 0:
                    return_val += 'y' + str(i) + '| '
                return_val += (str(self.board[j][i]['level']) +
                               str(self.board[j][i]['occupant']) +
                               ' ')
            return_val += '\n'
        return return_val

    def randomize_placement(self, color):
        """Randomly place the two gray pieces on the board."""
        potential_li = []  # list of potential spaces
        all_spaces = [(i, j) for i in range(1,3,1) for j in range(1,3,1)]

        # For all spaces, get the adjacent space
        for i, j in all_spaces:
            adjacent = get_adjacent(i, j)
            adjacent = filter(lambda x: x[0] in range(1,3) and x[1] in range(1,3), adjacent)
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
                self.turn += 2
                chose_spaces = True

    def get_board_score(self, color='W'):
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
        other_color = get_opponent_color(color)

        score = 0
        spaces = [(i, j) for i in range(5) for j in range(5)]
        for i, j in spaces:
            space = self.board[i][j]
            adjacent_spaces = get_moveable_spaces(game=self, space=(i, j))

            # 4^level for occupied spaces, 2^level for adjacent spaces
            # in both cases, negative points given for opponent pieces
            if space['occupant'] == color:
                score += 4 ** space['level']
            elif space['occupant'] == other_color:
                score -= 4 ** space['level']

            for k, l in adjacent_spaces:
                space = self.board[k][l]
                if space['occupant'] == color and space['level'] != 4:
                    score += 2 ** space['level']
                elif space['occupant'] == other_color and space['level'] != 4:
                    score -= 2 ** space['level']
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
        switchcolor : bool, optional
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
        for i, j in SPACE_LIST:
            self.board[i][j]['active'] = self.board[i][j]['occupant'] == self.color

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

    def make_exterior_active(self):
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

    def place(self, color, x_val, y_val):  # Only runs at beginning of game
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
            self.turn += 1
            return True
        return False

    def select(self, color, x_val, y_val):
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

    def move_worker(self, x_val, y_val, auto = False):
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
            self.make_exterior_active()
            return True

    def build_level(self, x_val, y_val, auto = False):
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
            self.select(self.color, x_val, y_val)
        elif self.sub_turn == 'move':  # Moving that piece
            self.check_move_available()
            self.move_worker(x_val, y_val)
        elif self.sub_turn == 'build':
            self.build_level(x_val, y_val)

    def play_automatic_turn(self, move_color, eval_color=None, tree_depth=DEPTH):
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
        tree_depth = int(tree_depth)
        if tree_depth <= 2:
            tree_depth = 2

        game_copy = deepcopy(self)
        root_node = Node(game=game_copy,
                         children=[])

        best_state = alpha_beta_move_selection(root_node=root_node, depth=tree_depth,
                                               move_color=move_color, eval_color=eval_color)[1]

        self.board = best_state.game.board
        self.end = best_state.game.end
        if not self.end:
            self.sub_turn = 'switch'


def alpha_beta_move_selection(root_node, depth, alpha = -10 ** 5, beta =10 ** 5, move_color='G', eval_color='G', is_max=True):
    # End game, don't need to check child nodes
    if root_node.game.end:
        if eval_color != move_color:
            return 10 ** 5, None
        else:
            return -10 ** 5, None

    if depth == 0:
        return root_node.game.get_board_score(get_opponent_color(move_color)), None

    potential_nodes = create_potential_moves(node=root_node, move_color=move_color, eval_color=eval_color)
    best_node = potential_nodes[0]

    if is_max:
        current_value = -10 ** 5

        for node in potential_nodes:
            node.game.color = get_opponent_color(move_color)
            results = alpha_beta_move_selection(root_node = node, depth =depth - 1, alpha = alpha, beta = beta,
                                                move_color=get_opponent_color(move_color), eval_color=eval_color,
                                                is_max = not is_max)

            if current_value < results[0]:
                current_value = results[0]
                alpha = max(alpha, current_value)
                best_node = node

            if beta <= alpha:
                break

        if best_node is None:
            return current_value, None

    else:
        current_value = 10 ** 5
        for node in potential_nodes:
            node.game.color = get_opponent_color(move_color)
            results = alpha_beta_move_selection(root_node=node, depth=depth - 1, alpha=alpha, beta=beta,
                                                move_color=get_opponent_color(move_color), eval_color=eval_color,
                                                is_max=not is_max)

            if current_value > results[0]:
                current_value = results[0]
                beta = min(beta, current_value)
                best_node = node

            if beta <= alpha:
                break

        if best_node is None:
            return current_value, None

    return current_value, best_node


def get_moveable_spaces(game, space):
    return_li = []
    x_val, y_val = space
    height = game.board[x_val][y_val]['level']
    for spot in get_adjacent(x_val, y_val):
        x_adj, y_adj = spot
        if (game.board[x_adj][y_adj]['occupant'] == 'O' and
                (game.board[x_adj][y_adj]['level'] - height) <= 1):
            return_li.append((x_adj, y_adj))

    return iter(return_li)


def get_buildable_spaces(game, space):
    return_li = []
    x_val, y_val = space
    for spot in get_adjacent(x_val, y_val):
        x_adj, y_adj = spot
        if (game.board[x_adj][y_adj]['occupant'] == 'O'):
            return_li.append((x_adj, y_adj))

    return iter(return_li)


def create_potential_moves(node, move_color, eval_color, depth = 1):
    """
    Add list of possible moves to game state.
    Parameters
    ----------
    game : Game
        Game fomr which to attempt moves
    move_color : char, optional
        Player color, G(ray) or W(hite). The default is 'G'.
    level : char, optional
        what level of the tree board takes place on
        Root node is level 0, its children are level 1,
        children of those children are level 2 etc. The default is 0.
    Returns
    -------
    return_li : list
        Children of that node
    """
    return_li = []
    # Check both of the spaces occupied by the player
    for spot in [(i, j) for i in range(5) for j in range(5) if
                 node.game.board[i][j]['occupant'] == move_color]:
        i, j = spot
        # check each possible move

        for space in get_moveable_spaces(game=node.game, space=(i, j)):

            new_game = Game()
            new_game = game_deep_copy(node.game, move_color)
            new_game.select(move_color, i, j)

            new_game.move_worker(space[0], space[1], auto = True)
            if new_game.end:
                return_li.append(Node(
                    game=new_game,
                    score=new_game.get_board_score(move_color),
                    parent=node))
            else:
                # given a legal move, check for each possible build
                for build in get_buildable_spaces(new_game, (new_game.col, new_game.row)):
                    build_game = game_deep_copy(new_game,
                                                new_game.color)

                    build_game.build_level(build[0], build[1], auto = True)
                    if build_game.end:
                        new_score = build_game.get_board_score(eval_color)
                    else:
                        new_score = 0

                    return_li.append(Node(
                        game=build_game,
                        score=new_score,
                        parent=node))

    # Sort by highest score for your moves, lowest for opponent moves
    return_li = sorted(return_li, key=lambda x: x.score * -1)

    return return_li


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

    return new_game


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


def get_adjacent(x_val, y_val, when='general'):
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
    if when == 'general':
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
