class Player():
    """
    Player of the Game class.
    
    Placeholder line for variables
    """
    
    def __init__(self, game, player_type = 'human', color = 'W'):
        self.game = game
        self.color = color
        self.player_type = player_type
        self.placements = 0
        #self.game.sub_turn = 'place'
    
    def __str__(self):
        """Show string representation of player."""
        return (self.color + '-' + self.player_type + '-'
                + str(self.placements))
    
    def place_piece(self, x_coor = -1, y_coor = -1):
        """Manual or automatic palcement of piece on board."""
        if self.player_type == 'human':
            if self.game.place(self.color, x_coor, y_coor):
                    self.placements += 1
        elif self.player_type == 'alphabeta':
            self.game.randomize_placement(self.color)
            self.placements = 2
        
    def play_regular_turn(self, x_coor= -1, y_coor= -1):
        """Manual or auto play of turn, depending on player type."""
        if self.player_type == 'human':
            self.game.play_manual_turn(x_coor, y_coor)
        elif self.player_type == 'alphabeta':
            self.game.auto_play_turn(self.color)
            self.game.sub_turn = 'switch'
    
    def play_turn(self, x_coor = -1, y_coor = -1):
        """Test."""
        if self.placements >= 2:
            self.play_regular_turn(x_coor, y_coor)
        elif self.placements < 2:
            self.place_piece(x_coor, y_coor)
        
        if self.placements == 2 and self.game.sub_turn == 'place':
            print('test')
            self.game.sub_turn = 'switch'