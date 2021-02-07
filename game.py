# pylint: disable=E0633
from copy import deepcopy
import random
import datetime as dt
from node import Node, print_breadth_first, print_depth_first
import time

SYS_RANDOM = random.SystemRandom()
DEPTH = 2

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
    sub_turn : str
        action within a turn: place, select, move, or build
    message : str
        message given to player when they make an invalid choice
        not currently in action on on the pygame board
    """

    def __init__(self):
        self._board = [[{'level': 0, 'occupant': 'O', 'active': False}
                        for i in range(5)] for j in range(5)]
        self._row = 0
        self._col = 0
        self._end = False
        self._turn = 1
        self._sub_turn = 'place'
        self._message = ''
        self._color = 'W'

    def __str__(self):
        """
        Create ASCII representation of game state.

        Returns
        -------
        return_val : str
            ASCII represntation of the board
        """
        return_val = 'score: ' + str(self.evaluate_board()) + ' \n'
        return_val += "    x0 x1 x2 x3 x4\n"
        return_val += "    --------------\n"
        for i in range(5):
            for j in range(5):
                if j == 0:
                    return_val += 'y' + str(i) + '| '
                return_val += (str(self._board[j][i]['level']) +
                               str(self._board[j][i]['occupant']) +
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
            #debugging
            space1, space2 = SYS_RANDOM.sample(potential_li, k=1)[0]
            x_0, y_0 = space1
            x_1, y_1 = space2
            if (self._board[x_0][y_0]['occupant'] == 'O' and
                    self._board[x_1][y_1]['occupant'] == 'O'):
                self._board[x_0][y_0]['occupant'] = color
                self._board[x_1][y_1]['occupant'] = color
                self._turn += 2
                chose_spaces = True

    def evaluate_board(self):
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
        if self.color == 'W':
            other_color = 'G'
        else:
            other_color = 'W'

        score = 0
        spaces = [(i, j) for i in range(5) for j in range(5)]
        for i, j in spaces:
            space = self._board[i][j]
            adjacent_spaces = get_adjacent(i, j)

            # 3^level for occupied spaces, 2^level for adjacent spaces
            # in both cases, negative points given for opponent pieces
            if space['occupant'] == self._color:
                score += 4 ** space['level']
            elif space['occupant'] == self._color:
                score -= 4 ** space['level']
            for k, l in adjacent_spaces:
                space = self._board[k][l]
                if space['occupant'] == other_color:
                    score += 2 ** (space['level'] % 4)
                elif space['occupant'] == other_color:
                    score -= 2 ** (space['level'] % 4)
        return score

    def undo(self):
        """Undo select action."""
        self._sub_turn = 'select'
        self.make_color_active()

    def make_all_spaces_inactive(self):
        """Get rid of red boxes for all spaces."""
        for i in range(5):
            for j in range(5):
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
        height = self._board[x_coor][y_coor]['level']
        space_list = get_adjacent(x_coor, y_coor)
        for i, j in space_list:
            if (
                    is_valid_num(i) and is_valid_num(j) and
                    self._board[i][j]['occupant'] == 'O'
                    and self._board[i][j]['level'] - height <= 1
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
                    self._board[i][j]['occupant'] == 'O'):
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
        self._end = True
        if switch_color:
            if self._color == 'W':
                self._color = 'G'
            else: 
                self._color = 'W'

        # make all space inactive
        self.make_all_spaces_inactive()
        self._sub_turn = 'end'

    def make_color_active(self):
        """
        Mark pieces as active.

        For a given player color, mark all the spaces with that
        player color as active

        """
        for j in range(5):
            for i in range(5):
                if self._board[i][j]['occupant'] == self._color:
                    self._board[i][j]['active'] = True
                else:
                    self._board[i][j]['active'] = False

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
        for j in range(5):
            for i in range(5):
                self._board[i][j]['active'] = \
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
                self._board[i][j]['active'] = \
                    abs(i - self._col) <= 1 and \
                    abs(j - self._row) <= 1 and \
                    not(i == self._col and j == self._row) and \
                    self._board[i][j]['occupant'] == 'O'

    def check_move_available(self):
        """End game if player has no available moves."""
        for j in range(5):
            for i in range(5):
                if (self._board[i][j]['occupant'] == self._color and
                        self.is_valid_move_space(i, j)):
                    return  # end function if we have a valid space
        self.end_game(True)

    def check_build_available(self):
        """End game if player has no available builds."""
        for j in range(5):
            for i in range(5):
                if (
                        self._board[i][j]['occupant'] == self._color and
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
        if self._board[x_coor][y_coor]['occupant'] != 'O':
            self._message = "Occupied Space"
        else:
            self._board[x_coor][y_coor]['occupant'] = color
            self._turn += 1
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
        if self._board[x_coor][y_coor]['occupant'] != color:
            self._message = "You don't own that piece"
        else:
            self._col = x_coor
            self._row = y_coor
            self.make_choice_active(x_coor, y_coor)
            self._sub_turn = 'move'
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
        prev_col = self._col  # x
        prev_row = self._row  # y
        if abs(y_coor - prev_row) > 1 or \
           abs(x_coor - prev_col) > 1:
            self._message = "That space is too far away"
        elif y_coor == prev_row and x_coor == prev_col:
            self._message = "You must move"
        elif self._board[x_coor][y_coor]['occupant'] != 'O':
            self._message = "That spot is taken. Please choose another"
        elif self._board[x_coor][y_coor]['level'] - \
                self._board[prev_col][prev_row]['level'] > 1:
            self._message = "That spot is too high, please choose another"
        else:
            self._board[x_coor][y_coor]['occupant'] = self._color
            self._board[prev_col][prev_row]['occupant'] = 'O'
            if self._board[x_coor][y_coor]['level'] == 3:
                self.end_game()
            self._col = x_coor
            self._row = y_coor
            self._sub_turn = 'build'
            self.make_exterior_active()
            return True
        return False

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
        if abs(y_coor - self._row) > 1 or \
           abs(x_coor - self._col) > 1:
               pass
            #self._message = "That space is too far away"
        elif y_coor == self._row and x_coor == self._col:
            pass
            #self._message = "Can't build on your own space"
        elif self._board[x_coor][y_coor]['occupant'] != 'O':
            pass
            #self._message = "That spot is taken. Please choose another\n"
            self._row = y_coor
            self._col = x_coor
        else:
            self._board[x_coor][y_coor]['level'] += 1
            if self._board[x_coor][y_coor]['level'] == 4:
                self._board[x_coor][y_coor]['occupant'] = 'X'
            self._sub_turn = 'switch'
            return True
        return False

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
        if self._sub_turn == 'select':  # Selecting which piece to move
            self.make_color_active()
            self.select(self._color, x_coor, y_coor)
        elif self._sub_turn == 'move':  # Moving that piece
            self.check_move_available()
            self.move(x_coor, y_coor)
        elif self._sub_turn == 'build':
            self.build(x_coor, y_coor)

    @property
    def sub_turn(self):
        """Return sub_turn."""
        return self._sub_turn

    @property
    def turn(self):
        """Return turn."""
        return self._turn

    @property
    def end(self):
        """Return end variable."""
        return self._end

    @property
    def col(self):
        """Return col(umn) variable."""
        return self._col

    @property
    def row(self):
        """Return row variable."""
        return self._row

    @property
    def color(self):
        """Return color variable."""
        return self._color

    @property
    def board(self):
        """Return board in its current state."""
        return self._board

    @board.setter
    def board(self, board):
        """Change board, used for AI's moves."""
        self._board = board

    @sub_turn.setter
    def sub_turn(self, sub_turn):
        """Change board, used for AI's moves."""
        self._sub_turn = sub_turn

    @color.setter
    def color(self, color):
        """Set color of game."""
        self._color = color
    
    def play_automatic_turn(self, color, tree_depth = DEPTH):
        """
        Make automatic turn.

        Uses alpha-beta pruning to selection best turn
        and update game object to that ideal turn
        """
        if tree_depth <= 2:
            tree_depth = 2
        tree_depth = int(tree_depth)
        
        game_copy = deepcopy(self)
        root_node = Node(game=game_copy,
                         children=[],
                         level=0,
                         max_level = tree_depth)
        
        create_children_recursive(root_node)
        
        #print_breadth_first(root_node)
        
        best_state = root_node.alpha_beta_search()
        self._board = best_state.board
        self._end = best_state.end
        if not self._end:
            self._sub_turn = 'switch'

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

def get_adjacent(x_coor, y_coor, when = 'general'):
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

def create_children(node, color='G'):
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
                 node.game._board[i][j]['occupant'] == color]:
        i, j = spot
        # check each possible move
        
        for space in iter(filter(lambda s: 
                             node.game._board[s[0]][s[1]]['occupant']
                             == 'O'
                             ,get_adjacent(i, j))):
            
            #new_game = deepcopy(node.game)            
            new_game = Game()
            new_game._board = deepcopy(node.game._board)
            #new_game._color = color
            new_game._end = node.game._end
            new_game._col = node.game._col
            new_game._row = node.game._row
            new_game.select(color, i, j)
            
            if new_game.move(space[0], space[1]):
                print(new_game)
            # given a legal move, check for each possible build
                for build in iter(
                        filter(lambda s: 
                        new_game._board[s[0]][s[1]]['occupant'] == 'O'
                             ,get_adjacent(new_game.col,
                                          new_game.row))):
                    
                    build_game = Game()
                    build_game._board = deepcopy(new_game._board)
                    build_game._end = new_game._end
                    build_game._col = new_game._col
                    build_game._row = new_game._row
                                        
                    if build_game._end:
                        return_li.append(Node(
                            game=build_game,
                            level=node.level + 1,
                            max_level=node.max_level))
                    
                    elif (build_game is not None and 
                          build_game.build(build[0], build[1])):
                        return_li.append(Node(
                            game=build_game,
                            level=node.level + 1,
                            max_level=node.max_level))
    return return_li

def create_children_recursive(node):
    """
    Create future turns, plus future turns for those future turns.
    
    Recursive function. root node will contain a "max level"
    value, which will tell this function when to stop

    Parameters
    ----------
    node : Node
        Nodes with which to create child nodes (ie subsequent turns)
    """
    # for even numbered levels, move the other color
    if node.level % 2 == 0:
        color = node.game.color
    else:
        if node.game.color == 'G':
            color = 'W'
        else:
            color = 'G'
    
    # recurring case, note that create_children increments the level
    if node.level < node.max_level:
        node.children = create_children(node, color)
        for child in node.children:
            create_children_recursive(child)