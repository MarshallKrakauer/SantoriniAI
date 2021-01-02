from tree_traversal import Node, level_order
import copy
import time
import datetime as dt

# This is a comment

class Game():
    
    def __init__(self):
        self._board = [[{'level' : 0, 'occupant' : 'O', 'active' : False} 
                       for i in range(0,5)] for j in range(0,5)]
        self._row = 0
        self._col = 0
        self._end = False
        self._color = 'G'
        self._turn = 1
        self._sub_turn = 'select'
        self._message = ''

    def evaluate_board(self):
        score = 0
        spaces = [(i, j) for i in range(5) for j in range(5)]
        for i, j in spaces:
            space = self._board[i][j]
            adjacent_spaces = self.get_adjacent(i, j)
            if space['occupant'] == 'G':
                score += 3  ** space['level']
            elif space['occupant'] == 'W':
                score -= 3 ** space['level']
            for k, l in adjacent_spaces:
                space = self._board[k][l]
                if space['occupant'] == 'G':
                    score += 2  ** (space['level'] % 4)
                elif space['occupant'] == 'W':
                    score -= 2 ** (space['level'] % 4)
        return score        
    
    def get_adjacent(self,x,y):
        spaceLi = [(x - 1, y + 1), (x, y + 1), (x + 1, y + 1),
                     (x - 1, y), (x + 1 , y ),
                     (x - 1, y - 1), (x, y - 1), (x + 1, y- 1)]
        spaceLi = list(filter(
                        lambda t: t[0] >= 0 and t[0] <= 4 
                              and t[1] >= 0 and t[1] <= 4,
                   spaceLi))
        
        return spaceLi
    
    def create_children(self, color = 'G', level = 0):
        return_li = []
        buildLi = []
        moveLi = []     
        spotLi = [(i,j) for i in range(5) for j in range(5) if 
                   self._board[i][j]['occupant'] == color]
        for spot in spotLi:
            i, j = spot
            moveLi = self.get_adjacent(i,j) # available moves
            
            #check each possible move
            for m in moveLi:
                newGame = copy.deepcopy(self)
                newGame._color = color
                newGame.select(newGame.color, i, j)
                if newGame.move(x = m[0], y = m[1]):
                    buildLi = self.get_adjacent(newGame.col,
                                                newGame.row)
                # given a legal move, check for each possible build
                    for b in buildLi:
                        buildGame = copy.deepcopy(newGame)
                        if buildGame.build(x = b[0], y = b[1]):
                            nodeGame = copy.deepcopy(buildGame)
                            currentNode = Node(
                                value = nodeGame.evaluate_board(),
                                children = [],
                                state = nodeGame,
                                level = level + 1)
                            return_li.append(currentNode)
        return return_li
    
    def future_moves(self):
        gameCopy = copy.deepcopy(self)        
        rootNode = Node(value = gameCopy.evaluate_board(),
                        state = gameCopy,
                        children = [],
                        level = 0)
        rootNode.children = gameCopy.create_children('G',0)
        for child in rootNode.children:
            childCopy = copy.deepcopy(child.state)
            child.children = childCopy.create_children('W', 1)
            print(child.children)
        
        best_state = rootNode.alpha_beta_search()
        self._board = best_state._board
        self._end = best_state._end
        if not self._end:
            self.switch_player()
            self.make_color_active()
            self._sub_turn = 'select'
        return True            
        
    def __str__(self):
        return_val = 'score: ' + str(self.evaluate_board()) + ' \n'
        for y in range(5):
            if y == 0: 
                return_val += "    x0 x1 x2 x3 x4\n"
                return_val += "    --------------\n"
            for x in range(5):
                if x == 0:
                    return_val += 'y' + str(y) + '| '
                return_val += (str(self._board[x][y]['level']) +
                              str(self._board[x][y]['occupant']) +
                              ' ')
            return_val += '\n' 
        return return_val
    
    ### HELPER FUNCTIONS
    
    def is_valid_num(self,num):
        return num > -1 and num < 5
    
    def undo(self):
        self._sub_turn = 'select'
        self.make_color_active()
    
    def is_valid_move_space(self, x, y):
        height = self._board[x][y]['level']
        spaceList = self.get_adjacent(x, y)
        for i,j in spaceList:
            if (
            self.is_valid_num(i) and self.is_valid_num(j) and
            self._board[i][j]['occupant'] == 'O'
            and self._board[i][j]['level'] - height <= 1
            ):
                return True
        return False
    
    def is_valid_build_space(self, x, y):
        spaceList = self.get_adjacent(x, y)
        for i,j in spaceList:
            if (
            self.is_valid_num(i) and self.is_valid_num(j) and
            self._board[i][j]['occupant'] == 'O'):
                return True
        return False    
    
    def end_game(self, switchColor = False): 
        self._end = True
        if switchColor:
            self.switch_player()
        print(self._color , " WINS!")
        self._sub_turn = 'end'
   
    def switch_player(self):
        if self._color == 'G':
            self._color = 'W'
        else:
            self._color = 'G'
    
    #RED BOXES THAT HIGHLIGHT ACTIVE TURNS
    
    def make_color_active(self):
        for y in range(5):
            for x in range(5):
                if self._board[x][y]['occupant'] == self._color:
                    self._board[x][y]['active'] = True
                else:
                    self._board[x][y]['active'] = False
    
    def make_choice_active(self, x , y):
        for j in range(5):
            for i in range(5):
                self._board[i][j]['active'] = \
                    i == x and j == y
                    
    def make_exterior_active(self):
        # Check if each space represents a valid place to build
        for j in range(5):
            for i in range(5):
                self._board[i][j]['active'] = \
                    abs(i - self._col) <= 1 and \
                    abs(j - self._row) <= 1 and \
                    not(i == self._col and j == self._row) and \
                    self._board[i][j]['occupant'] == 'O'
    
    #CHECK IF USER HAS AVAILABLE MOVES
    
    def check_move_available(self):
        for j in range(5):
            for i in range(5):
                if (
                self._board[i][j]['occupant'] == self._color and
                self.is_valid_move_space(i,j)):
                    return # end function if we have a valid space
        self.end_game(True)
        
    def check_build_available(self):
        for j in range(5):
            for i in range(5):
                if (
                self._board[i][j]['occupant'] == self._color and
                self.is_valid_build_space(i,j)):
                    return # end function if we have a valid space
        self.end_game(True)
        
    # SUB-TURN PIECES
        
    def place(self, char): # Only runs at beginning of game
        y = self._row
        x = self._col
        if(self._board[x][y]['occupant'] != 'O'):
            self._message = "Occupied Space"
        else:
            self._board[x][y]['occupant'] = char
            self._turn += 1

    def select(self, color,x,y):
        if self._board[x][y]['occupant'] != color:
            self._message = "You don't own that piece"
            return False
        else:
            self._col = x
            self._row = y
            self.make_choice_active(self._col, self._row)
            self._sub_turn = 'move'
            return True
    
    def move(self, x, y):
        prev_row = self._row # y
        prev_col = self._col # x
        if abs(y - prev_row) > 1 or \
           abs(x - prev_col) > 1:
            self._message = "That space is too far away"
        elif y == prev_row and x == prev_col:
            self._message = "You must move"
        elif self._board[x][y]['occupant'] != 'O':
            self._message = "That spot is taken. Please choose another"
        elif self._board[x][y]['level']  - \
             self._board[prev_col][prev_row]['level']> 1:
            self._message = "That spot is too high, please choose another"
        else:
            self._board[x][y]['occupant'] = self._color
            self._board[prev_col][prev_row]['occupant'] = 'O'
            if self._board[x][y]['level'] == 3:
                self.end_game()
            self._col = x
            self._row = y
            self._sub_turn = 'build'
            self.make_exterior_active()
            '''
            self.switch_player()
            self.make_color_active()
            self._sub_turn = 'select'
            '''
            return True
        return False
    
    def build(self, x, y):
        if abs(y - self._row) > 1 or \
           abs(x - self._col) > 1:
               self._message = "That space is too far away"
        elif y == self._row and x == self._col:
            self._message = "Can't build on your own space"
        elif self._board[x][y]['occupant'] != 'O':
            self._message = "That spot is taken. Please choose another\n"
            self._row = y
            self._col = x
        else:
            self._board[x][y]['level'] += 1
            if(self._board[x][y]['level'] == 4):
                self._board[x][y]['occupant'] = 'X'
            self._sub_turn = 'switch'
            return True
        return False
    # THE PRIMARY FUNCTION THAT PLAYS THE ACTUAL GAME
    
    def play_turn(self, x , y):
        # Gray Places
        if self._turn in [1,2]:
            self.change_square(x, y)
            self.place('G')
        # White Places
        elif self._turn in [3,4]:
            self.change_square(x,y)
            self.place('W')
            
        # Playing the regular game
        elif self._turn > 4 and not self._end:
            if self._sub_turn == 'select': #Selecting which piece to move
                self.make_color_active()
                self.select(self._color, x, y)
            elif self._sub_turn == 'move': #Moving that piece
                self.check_move_available()
                self.move(x,y)
            elif self._sub_turn == 'build':
                self.build(x,y)
                if self._sub_turn == 'switch':
                    self.switch_player()
                    self.make_color_active()
                    self._sub_turn = 'select'
                    
    @property
    def sub_turn(self):
        return self._sub_turn
    
    @property
    def col(self):
        return self._col
    
    @property
    def row(self):
        return self._row
    
    @property
    def color(self):
        return self._color
    
    @property
    def board(self):
        return self._board
    
    @board.setter
    def board(self, board):
        self._board = board
    
    @color.setter
    def board(self, color):
        self._color = color
    
    #ACCESSORS
    
    def change_square(self, x, y):
        self._row = y
        self._col = x
    
    def get_board(self):
        return self._board
    
    def get_color(self) : 
        return self._color
    
    def get_turn(self):
        return self._turn
    
    def get_sub_turn(self):
        return self._sub_turn
    
    def get_end(self): 
        return self._end
