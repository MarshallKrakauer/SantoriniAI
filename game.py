# pylint: disable=E0633
from copy import deepcopy
import random
import datetime as dt
from node import Node, store_breadth_first
import time

SYS_RANDOM = random.SystemRandom()
SPACE_LIST = [(i, j) for i in range(5) for j in range(5)]
DEPTH = 3

class Game():
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
    subturn : str
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
        self.subturn = 'place'
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
        return_val = '' #'score: ' + str(self.evaluate_board()) + ' \n'
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
        all_spaces = [(i, j) for i in range(5) for j in range(5)]

        # For all spaces, get the adjacent space
        for i, j in all_spaces:
            adjacent = get_adjacent(i, j)
            for space in adjacent:
                potential_li.append(((i, j), space))

        # Choose random spaces until we have found one where both
        # spots are open
        chose_spaces = False
        while not chose_spaces:
            # debugging
            space1, space2 = SYS_RANDOM.sample(potential_li, k=1)[0]
            x_0, y_0 = space1
            x_1, y_1 = space2
            if (self.board[x_0][y_0]['occupant'] == 'O' and
                    self.board[x_1][y_1]['occupant'] == 'O'):
                self.board[x_0][y_0]['occupant'] = color
                self.board[x_1][y_1]['occupant'] = color
                self.turn += 2
                chose_spaces = True

    def evaluate_board(self, color = 'W'):
        """
        Give numeric score to game.

        Gives a score to the board based on position of the pices
        Used to for the alpha beta pruning algorith

        Returns
        -------
        score : int
            score of the board needed for alpha-beta pruning
            higher score is better
        """
        if color == 'W':
            other_color = 'G'
        else:
            other_color = 'W'

        score = 0
        spaces = [(i, j) for i in range(5) for j in range(5)]
        for i, j in spaces:
            space = self.board[i][j]
            adjacent_spaces = get_adjacent(i, j)

            # 3^level for occupied spaces, 2^level for adjacent spaces
            # in both cases, negative points given for opponent pieces
            if space['occupant'] == other_color:
                score += 4 ** space['level']
            elif space['occupant'] == color:
                score -= 4 ** space['level']
            # for k, l in adjacent_spaces:
            #     space = self.board[k][l]
            #     if space['occupant'] == color:
            #         score += 2 ** (space['level'] % 4)
            #     elif space['occupant'] == other_color:
            #         score -= 2 ** (space['level'] % 4)
        return score

    def undo(self):
        """Undo select action."""
        self.subturn = 'select'
        self.make_color_active()

    def make_all_spaces_inactive(self):
        """Get rid of red boxes for all spaces."""
        for i, j in SPACE_LIST:
            self.board[i][j]['active'] = False

    def is_valid_move_space(self, x_coor, y_coor):
        """
        Check if user made valid movement.

        Parameters
        ----------
        x_coor : int
            x coordinate of space
        y_coor : int
            y coordinate of space

        Returns
        -------
        bool
            true if move is valid, false if move is invalid
            for a move to be valid, it must be to an unoccupied space and
            no more than one level increase
        """
        height = self.board[x_coor][y_coor]['level']
        space_list = get_adjacent(x_coor, y_coor)
        for i, j in space_list:
            if (
                    is_valid_num(i) and is_valid_num(j) and
                    self.board[i][j]['occupant'] == 'O'
                    and self.board[i][j]['level'] - height <= 1
            ):
                return True
        return False

    def is_valid_build_space(self, x_coor, y_coor):
        """
        Check is user can build on chosen space.

        Parameters
        ----------
        x_coor : int
            x coordinate of space
        y_coor : int
            y coordinate of space

        Returns
        -------
        bool
            true if player can build there, false otherwise
            player can build on any unoccupied adjacent space
            not that spaces with a dome are considered occupied, with
            an occpant of X
        """
        space_list = get_adjacent(x_coor, y_coor)
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
        self.subturn = 'end'

    def make_color_active(self):
        """
        Mark pieces as active.

        For a given player color, mark all the spaces with that
        player color as active

        """
        for i, j in SPACE_LIST:
            if self.board[i][j]['occupant'] == self.color:
                self.board[i][j]['active'] = True
            else:
                self.board[i][j]['active'] = False

    def make_choice_active(self, x_coor, y_coor):
        """
        Mark the piece a player has chosen as active.

        Parameters
        ----------
        x_coor : int
            x coordinate of chosen piece
        y_coor : int
            y coordinate of chosen piece

        """
        for j, i in SPACE_LIST:
            self.board[i][j]['active'] = \
                i == x_coor and j == y_coor

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
                    not(i == self.col and j == self.row) and \
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

    def place(self, color, x_coor, y_coor):  # Only runs at beginning of game
        """
        Place two pieces of given color on the board.

        Parameters
        ----------
        color : str
            player color that will be placed on the board
        """
        if self.board[x_coor][y_coor]['occupant'] != 'O':
            self.message = "Occupied Space"
        else:
            self.board[x_coor][y_coor]['occupant'] = color
            self.turn += 1
            return True
        return False

    def select(self, color, x_coor, y_coor):
        """
        Choose piece to move.

        Parameters
        ----------
        color : str
            Color of current player
        x_coor : int
            x coordinate of spot on board
        y_coor : int
            y coordinate of spont on board

        Returns
        -------
        bool
            True/false if move is valid

        """
        if self.board[x_coor][y_coor]['occupant'] != color:
            self.message = "You don't own that piece"
        else:
            self.col = x_coor
            self.row = y_coor
            self.make_choice_active(x_coor, y_coor)
            self.subturn = 'move'
            return True
        return False

    def move(self, x_coor, y_coor):
        """
        Move piece to new spot on board.

        Parameters
        ----------
        x_coor : int
            x-coordinate
        y_coor : int
            y-coordinate

        Returns
        -------
        bool
            True if move is valid
        """
        prev_col = self.col  # x
        prev_row = self.row  # y
        if (abs(y_coor - prev_row) > 1 or
            abs(x_coor - prev_col) > 1) or \
            y_coor == prev_row and x_coor == prev_col or \
            self.board[x_coor][y_coor]['occupant'] != 'O' or \
            (self.board[x_coor][y_coor]['level'] -
                self.board[prev_col][prev_row]['level'] > 1):
                return False
        else:
            self.board[x_coor][y_coor]['occupant'] = self.color
            self.board[prev_col][prev_row]['occupant'] = 'O'
            if self.board[x_coor][y_coor]['level'] == 3:
                self.end_game()
            self.col = x_coor
            self.row = y_coor
            self.subturn = 'build'
            self.make_exterior_active()
            return True

    def build(self, x_coor, y_coor):
        """
        Build on a space.

        Parameters
        ----------
        x_coor : int
            x coordinate
        y_coor : int
            y coordinate

        Returns
        -------
        bool
            True if move is valid
        """
        if (abs(y_coor - self.row) > 1 or
                abs(x_coor - self.col) > 1) or \
                y_coor == self.row and x_coor == self.col or \
                self.board[x_coor][y_coor]['occupant'] != 'O':
            return False
        else:
            self.board[x_coor][y_coor]['level'] += 1
            if self.board[x_coor][y_coor]['level'] == 4:
                self.board[x_coor][y_coor]['occupant'] = 'X'
            self.subturn = 'switch'
            return True

    def play_manual_turn(self, x_coor, y_coor):
        """
        Run through a turn.

        After the piece placement has taken place, goes through
        motion of a normal turn.

        Parameters
        ----------
        x_coor : int
            x coordinate
        y_coor : int
            y coordinate
        """
        # Playing the regular game
        if self.subturn == 'select':  # Selecting which piece to move
            self.make_color_active()
            self.select(self.color, x_coor, y_coor)
        elif self.subturn == 'move':  # Moving that piece
            self.check_move_available()
            self.move(x_coor, y_coor)
        elif self.subturn == 'build':
            self.build(x_coor, y_coor)

    def play_automatic_turn(self, color, tree_depth=DEPTH):
        """
        Make automatic turn.

        Uses alpha-beta pruning to selection best turn
        and update game object to that ideal turn
        """
        tree_depth = int(tree_depth)
        if tree_depth <= 2:
            tree_depth = 2

        game_copy = deepcopy(self)
        root_node = Node(game=game_copy,
                         children=[],
                         level=0,
                         max_level=tree_depth)
        
        time1 = dt.datetime.now()
        create_game_tree(root_node)
        print("Tree creation time:", dt.datetime.now() - time1)
        
        if DEPTH <= 3:
            store_breadth_first(root_node)
        
        time1 = dt.datetime.now()
        best_state = root_node.alpha_beta_search()
        print("Alpha Beta Time:", dt.datetime.now() - time1)
        self.board = best_state.board
        self.end = best_state.end
        if not self.end:
            self.subturn = 'switch'


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


def get_adjacent(x_coor, y_coor, when='general'):
    """
    Get spaces surrounding the passed one.

    Parameters
    ----------
    x_coor : int
        x_coor-coordinate ie column value
    y_coor : int
        y_coor-coordinate ie row value

    Returns
    -------
    spaceLi : li
        list of spaces adjacent to the one provided through
        x_coor and y_coor
    """
    if when == 'general':
        space_list = [(x_coor - 1, y_coor + 1),
                      (x_coor, y_coor + 1),
                      (x_coor + 1, y_coor + 1),
                      (x_coor - 1, y_coor),
                      (x_coor + 1, y_coor),
                      (x_coor - 1, y_coor - 1),
                      (x_coor, y_coor - 1),
                      (x_coor + 1, y_coor - 1)]
        space_list = list(filter(
            lambda t: t[0] >= 0 and t[0] <= 4
            and t[1] >= 0 and t[1] <= 4,
            space_list))

    return space_list


def create_potential_moves(node, color='G'):
    """
    Add list of possible moves to game state.

    Parameters
    ----------
    game : Game
        Game fomr which to attempt moves
    color : char, optional
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
                 node.game.board[i][j]['occupant'] == color]:
        i, j = spot
        # check each possible move

        for space in get_adjacent(i, j):

            new_game = game_deep_copy(node.game, color)
            new_game.select(color, i, j)

            if new_game.move(space[0], space[1]):
                if new_game.end:
                    return_li.append(Node(
                        game=new_game,
                        level=node.level + 1,
                        max_level=node.max_level,
                        score  = new_game.evaluate_board(color),
                        parent = node))
                else:
                # given a legal move, check for each possible build
                    for build in get_adjacent(new_game.col, \
                                                      new_game.row):
                        build_game = game_deep_copy(new_game,
                                                     new_game.color)
    
                        if build_game.build(build[0], build[1]):
                            return_li.append(Node(
                                    game=build_game,
                                    level=node.level + 1,
                                    max_level=node.max_level,
                                    score = build_game.evaluate_board(color),
                                    parent = node))
        return_li = sorted(return_li, key=lambda x: x.score)
    return return_li


def create_game_tree(node):
    """
    Create future turns, plus future turns for those future turns.

    Recursive function. root node will contain a "max level"
    value, which will tell this function when to stop

    Parameters
    ----------
    node : Node
        Nodes with which to create child nodes (ie subsequent turns)
    """
    #for even numbered levels, move the other color
    
    if node.level % 2 == 0:
        color = node.game.color
    else:
        if node.game.color == 'G':
            color = 'W'
        else:
            color = 'G'

    # recurring case, note that create_children increments the level
    if node.level < node.max_level:
        node.children = create_potential_moves(node, color)
        for child in node.children:
            create_game_tree(child)


def game_deep_copy(game, color):
    """
    Deep copies board from another game.

    Used as part of the create children functions. Standard
    Python copy.deepcopy was too slow.

    Parameters
    ----------
    otherboard : list
        board from which to copy info

    Returns
    -------
    newboard : list
        new board with same info as otherboard

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
