"""Individual playing Santorini game. Needs a refactor to replace complexity."""


class Player:
    """
    Player of the Game class.

    Placeholder line for variables
    """

    def __init__(self, game, player_type='human', color='W'):
        self.game = game
        self.color = color
        self.player_type = player_type
        self.placements = 0

    def __str__(self):
        """Show string representation of player."""
        return (self.color + '-' + self.player_type + '-'
                + str(self.placements))

    def play_turn(self, x_val=-1, y_val=-1):
        """Place or play depending on turn."""
        self.game.color = self.color

        if self.placements >= 2:
            self.play_regular_turn(x_val, y_val)

        elif self.placements < 2:
            self.place_piece(x_val, y_val)

        if self.placements == 2 and self.game.sub_turn == 'place':
            self.game.sub_turn = 'switch'

    def place_piece(self, x_val=-1, y_val=-1):
        """Manual or automatic placement of piece on board."""
        if self.player_type == 'human':
            if self.game.place_worker(self.color, x_val, y_val):
                self.placements += 1
        elif self.player_type == 'alphabeta':
            self.game.randomize_placement(self.color)
            self.placements = 2

    def play_regular_turn(self, x_val=-1, y_val=-1):
        """Manual or auto play of turn, depending on player type."""
        if self.player_type == 'human':
            self.game.play_manual_turn(x_val, y_val)

        elif self.player_type == 'alphabeta':
            self.game.play_automatic_turn(move_color=self.color, eval_color=self.color)
            self.game.sub_turn = 'switch'

    def update_game(self):
        """Set up next player after turn switches."""
        self.game.color = self.color
        if self.placements >= 2:
            self.game.sub_turn = 'select'
            if self.player_type == 'human':
                self.game.make_color_active()
            else:
                self.game.make_all_spaces_inactive()
        else:
            self.game.sub_turn = 'place'

    def should_switch_turns(self):
        """Check if player is done with their turn."""
        return self.game.sub_turn == 'switch'

    def can_player_undo(self):
        """Check if player can undo selection."""
        return self.player_type == 'human' and self.game.sub_turn == 'move'
