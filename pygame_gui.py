# pylint: disable=E1101
"""pygame interaction with Santorini game."""

import pygame
import pygame.freetype

from button import Button
from game import Game
from santorini_player import SantoriniPlayer

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (190, 190, 190)
GOLD = (100, 84.3, 0)
LIGHT_GREEN = (30, 250, 150)

# Horizontal and vertical start of board
BOARD_TOP_EDGE = 100  # SIZE = (800, 600) #(width <-->, height)
BOARD_LEFT_EDGE = 275
BUTTON_MEASURES = [BOARD_LEFT_EDGE + 75, BOARD_TOP_EDGE + 350, 120, 60]
# Left_edge,             top_edge,             width, height

# Set up the pygame environment
pygame.init()
SIZE = (800, 600)  # (width <-->, height)
SCREEN = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Santorini")
font = pygame.font.SysFont('Calibri', 16, True, False)


def map_numbers(x_val, y_val):
    """
    Convert coordinates to board spaces.

    Parameters
    ----------
    x_val : int
        x coordinate of area that was clicked
    y_val : int
        y coordinate of area that was clicked

    Returns
    -------
    tuple
    area on board that was clicked

    """
    x_1 = (x_val - BOARD_LEFT_EDGE) // 50
    y_1 = (y_val - BOARD_TOP_EDGE) // 50
    return x_1, y_1


def check_valid(num):
    """Return true if valid board spot."""
    return -1 < num < 5


def end_fanfare(color='W'):
    """Produce visual showing who won the game. Returns the winner button for click detection."""
    text_color = WHITE if color == 'W' else GRAY
    winner_button = Button((BUTTON_MEASURES[0] + 50, BUTTON_MEASURES[1] + 20),
                           "WINNER: " + color, 40, BLUE, text_color, 1.2)
    winner_button.draw()
    return winner_button


def check_undo(x_val, y_val):
    """Return true if undo button was selected."""
    return (BOARD_LEFT_EDGE + 75 <= x_val <= BOARD_LEFT_EDGE + 180
            and BOARD_TOP_EDGE + 350 <= y_val <= BOARD_TOP_EDGE + 375)


def make_undo_button(player):
    """Show undo button in player color."""
    if player.color == 'W':
        button_color = WHITE
    else:
        button_color = GRAY
    undo_button = Button((BUTTON_MEASURES[0] + 50, BUTTON_MEASURES[1] + 20),
                         "UNDO", 40, button_color, BLUE, 1.5)
    undo_button.update(pygame.mouse.get_pos())
    undo_button.draw()


def draw_player_info(white_player, gray_player):
    """Draw player type labels above the board."""
    type_display = {'human': 'Human', 'alphabeta': 'Minimax', 'MCTS+RAVE': 'RAVE', 'MCTS': 'MCTS'}
    white_label = Button((100, 50), 'WHITE: ' + type_display.get(white_player.player_type, ''), 30, BLUE, WHITE, 1)
    gray_label = Button((700, 50), 'GRAY: ' + type_display.get(gray_player.player_type, ''), 30, BLUE, GRAY, 1)
    white_label.draw()
    gray_label.draw()


def draw_board(board):
    """Draw the 5x5 game board with player pieces."""
    for i in range(5):
        for j in range(5):
            vertical = BOARD_LEFT_EDGE + 50 * i
            horizontal = BOARD_TOP_EDGE + 50 * j
            pygame.draw.rect(SCREEN, WHITE,
                             [vertical, horizontal, 50, 50], 2)
            # Draw piece or dome

            # Draw occupant
            if board[i][j]['occupant'] == 'X':
                pygame.draw.rect(SCREEN, BLACK,
                                 [vertical, horizontal, 50, 50], 0)
            elif board[i][j]['occupant'] == 'G':
                pygame.draw.circle(SCREEN, GRAY,
                                   [vertical + 25, horizontal + 25], 50 / 3)
            elif board[i][j]['occupant'] == 'W':
                pygame.draw.circle(SCREEN, WHITE,
                                   [vertical + 25, horizontal + 25], 50 / 3)
            # Draw Active space
            if board[i][j]['active']:
                pygame.draw.rect(SCREEN, RED,
                                 [vertical, horizontal, 50, 50], 3)
            # Draw Winning Space
            if (board[i][j]['level'] == 3
                    and board[i][j]['occupant'] != 'O'):
                # noinspection PyTypeChecker
                pygame.draw.rect(SCREEN, GOLD,
                                 [vertical, horizontal, 50, 50], 5)

            # Draw height
            text = font.render(str(board[i][j]['level']), True, BLACK)
            SCREEN.blit(text, (vertical + 20, horizontal + 20))


def choose_arrow_location(x_val, y_val):
    """Draw arrow onto start screen."""
    pygame.draw.polygon(SCREEN,
                        RED,
                        # Locations to draw
                        ((12 + x_val, 112 + y_val),
                         (12 + x_val, 137 + y_val),
                         (62 + x_val, 137 + y_val),
                         (62 + x_val, 162 + y_val),
                         (87 + x_val, 125 + y_val),
                         (62 + x_val, 87 + y_val),
                         (62 + x_val, 112 + y_val)
                         )
                        )


def get_title_screen_buttons():
    """Create title screen buttons.

    Returns
        dict: Container of all buttons needed to make title screen selection
    """
    return {'start': Button(
        center_position=(400, 520),
        font_size=75,
        bg_rgb=GREEN,
        text_rgb=BLACK,
        text="CLICK TO START",
        multiplier=1), 'white header': Button(
        center_position=(200, 80),
        font_size=72,
        bg_rgb=BLUE,
        text_rgb=WHITE,
        text='WHITE',
        multiplier=1), 'gray header': Button(
        center_position=(600, 80),
        font_size=72,
        bg_rgb=BLUE,
        text_rgb=GRAY,
        text='GRAY',
        multiplier=1.2), 'white human': Button(
        center_position=(200, 160),
        font_size=40,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='Human',
        multiplier=1.2), 'gray human': Button(
        center_position=(600, 160),
        font_size=40,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='Human',
        multiplier=1.2), 'white minimax': Button(
        center_position=(200, 235),
        font_size=40,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='Minimax',
        multiplier=1.2), 'gray minimax': Button(
        center_position=(600, 235),
        font_size=40,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='Minimax',
        multiplier=1.2), 'white MCTS+RAVE': Button(
        center_position=(200, 310),
        font_size=40,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='RAVE',
        multiplier=1.2), 'gray MCTS+RAVE': Button(
        center_position=(600, 310),
        font_size=40,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='RAVE',
        multiplier=1.2), 'white MCTS': Button(
        center_position=(200, 385),
        font_size=40,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='MCTS',
        multiplier=1.2), 'gray MCTS': Button(
        center_position=(600, 385),
        font_size=40,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='MCTS',
        multiplier=1.2)}


def draw_title_screen_material(arrow_dict, button_dict, counter):
    # Choose where to show red arrow for white piece
    if arrow_dict['white human']:
        choose_arrow_location(30, 160 - 124)
    elif arrow_dict['white minimax']:
        choose_arrow_location(30, 235 - 124)
    elif arrow_dict['white MCTS+RAVE']:
        choose_arrow_location(30, 310 - 124)
    elif arrow_dict['white MCTS']:
        choose_arrow_location(30, 385 - 124)

    # Choose where to show red arrow for gray piece
    if arrow_dict['gray human']:
        choose_arrow_location(410, 160 - 124)
    elif arrow_dict['gray minimax']:
        choose_arrow_location(410, 235 - 124)
    elif arrow_dict['gray MCTS+RAVE']:
        choose_arrow_location(410, 310 - 124)
    elif arrow_dict['gray MCTS']:
        choose_arrow_location(410, 385 - 124)

    # Show start button if all choices have been made
    white_chosen = arrow_dict['white human'] | arrow_dict['white minimax'] | arrow_dict['white MCTS+RAVE'] | arrow_dict['white MCTS']
    gray_chosen = arrow_dict['gray human'] | arrow_dict['gray minimax'] | arrow_dict['gray MCTS+RAVE'] | arrow_dict['gray MCTS']
    if white_chosen and gray_chosen and counter % 2500 < 1500:
        button_dict['start'].draw()

    # Draw all buttons
    for button in button_dict.keys():
        if button != 'start':
            button_dict[button].draw()


def title_screen():
    """Show title screen before playing."""
    counter = 0

    button_dict = get_title_screen_buttons()
    arrow_dict = {'white human': False, 'white minimax': False, 'white MCTS+RAVE': False, 'white MCTS': False,
                  'gray human': False, 'gray minimax': False, 'gray MCTS+RAVE': False, 'gray MCTS': False}
    end_loop = False

    while not end_loop:
        SCREEN.fill(LIGHT_GREEN)

        # Update arrows + show start screen if it's ready
        draw_title_screen_material(arrow_dict, button_dict, counter)

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()

            # Check if mouse is hovering over any of the buttons
            for button in button_dict:
                if button not in ['start', 'white header', 'gray header']:
                    button_dict[button].update(pos)

            # Move red arrow based on selection for white
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_dict['white human'].check_press(pos):
                    arrow_dict.update({'white human': True, 'white minimax': False, 'white MCTS+RAVE': False, 'white MCTS': False})
                elif button_dict['white minimax'].check_press(pos):
                    arrow_dict.update({'white human': False, 'white minimax': True, 'white MCTS+RAVE': False, 'white MCTS': False})
                elif button_dict['white MCTS+RAVE'].check_press(pos):
                    arrow_dict.update({'white human': False, 'white minimax': False, 'white MCTS+RAVE': True, 'white MCTS': False})
                elif button_dict['white MCTS'].check_press(pos):
                    arrow_dict.update({'white human': False, 'white minimax': False, 'white MCTS+RAVE': False, 'white MCTS': True})

                if button_dict['gray human'].check_press(pos):
                    arrow_dict.update({'gray human': True, 'gray minimax': False, 'gray MCTS+RAVE': False, 'gray MCTS': False})
                elif button_dict['gray minimax'].check_press(pos):
                    arrow_dict.update({'gray human': False, 'gray minimax': True, 'gray MCTS+RAVE': False, 'gray MCTS': False})
                elif button_dict['gray MCTS+RAVE'].check_press(pos):
                    arrow_dict.update({'gray human': False, 'gray minimax': False, 'gray MCTS+RAVE': True, 'gray MCTS': False})
                elif button_dict['gray MCTS'].check_press(pos):
                    arrow_dict.update({'gray human': False, 'gray minimax': False, 'gray MCTS+RAVE': False, 'gray MCTS': True})

            # If both choices have been made, show the start button
            white_chosen = arrow_dict['white human'] | arrow_dict['white minimax'] | arrow_dict['white MCTS+RAVE'] | arrow_dict['white MCTS']
            gray_chosen = arrow_dict['gray human'] | arrow_dict['gray minimax'] | arrow_dict['gray MCTS+RAVE'] | arrow_dict['gray MCTS']
            if white_chosen and gray_chosen:
                button_dict['start'].update(pos)

            # If person clicks start, start the game!
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_dict['start'].check_press(pos):
                    end_loop = True

            # Allow user to quit the game
            if event.type == pygame.QUIT:
                end_loop = True

        counter += 1
        pygame.display.flip()

    # default option if title screen is skipped (not currently possible, could be in the future)
    white_player, gray_player = 'alphabeta', 'alphabeta'

    if arrow_dict['white human']:
        white_player = 'human'
    elif arrow_dict['white minimax']:
        white_player = 'alphabeta'
    elif arrow_dict['white MCTS+RAVE']:
        white_player = 'MCTS+RAVE'
    elif arrow_dict['white MCTS']:
        white_player = 'MCTS'

    if arrow_dict['gray human']:
        gray_player = 'human'
    elif arrow_dict['gray minimax']:
        gray_player = 'alphabeta'
    elif arrow_dict['gray MCTS+RAVE']:
        gray_player = 'MCTS+RAVE'
    elif arrow_dict['gray MCTS']:
        gray_player = 'MCTS'

    return {'W': white_player, 'G': gray_player}


def play_human_turn(event, current_player, game, player_num, players):
    """
    Converts human click into play on the board

    Attributes
    ----------
    event : Pygame event
        Pygame interpretation of click or keyboard stroke

    current_player : Player object
        White or gray player based on current turn

    game : Game object
        Game that is currently being played

    player_num : int
        0 or 1 value corresponding to white or gray_player

    players : list
        list containing 2 player objects

    Returns
    -------
    current_player: char
        W or G, representing who shall make the next term
    player_num : int
        0 or 1, for the index of the current player
    players : list
        list containing both player objects
    """
    if event.type == pygame.MOUSEBUTTONDOWN and not game.end:
        pos = pygame.mouse.get_pos()
        x, y = map_numbers(pos[0], pos[1])

        if check_valid(x) and check_valid(y):
            current_player.play_turn(x, y)
            if current_player.should_switch_turns():
                player_num = (player_num + 1) % 2
                current_player = players[player_num]
                current_player.update_game()

        # Undo selection if chosen
        if check_undo(pos[0], pos[1]) and \
                current_player.can_player_undo():
            game.undo()

    return current_player, player_num, players


def play_ai_turn(current_player, player_num, players, show_board=True):
    """
    Plays the AI's turn

    Attributes
    ----------
    current_player : Player object
        White or gray player based on current turn

    player_num : int
        0 or 1 value corresponding to white or gray_player

    players : list
        list containing 2 player objects

    show_board : bool
        alternates between true and false every function call, needed to show board while function
        is thinking

    Returns
    -------
    current_player: char
        W or G, representing who shall make the next term
    player_num : int
        0 or 1, for the index of the current player
    players : list
        list containing both player objects
    show_board : bool
        Controls switch between updating board and showing the "thinking" tile
    """
    if current_player.color == 'W':
        button_color = WHITE
    else:
        button_color = GRAY
    thinking_message = Button((BUTTON_MEASURES[0] + 50, BUTTON_MEASURES[1] + 20),
                              "THINKING...", 40, button_color, BLUE, 1)
    thinking_message.draw()

    if show_board:
        current_player.play_turn()
        show_board = False
    else:
        show_board = True

    if current_player.should_switch_turns():
        player_num = (player_num + 1) % 2
        current_player = players[player_num]
        current_player.update_game()

    return current_player, player_num, players, show_board


def play_game(white_player, gray_player):
    """
    Create and run UI to play Santorini.

    Parameters
    ----------
    white_player : SantoriniPlayer
        Player object moving the white piece

    gray_player : SantoriniPlayer
        Player object moving the gray piece
    """
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()
    game_is_done = False  # ends pygame input when true
    return_to_menu = False  # true when winner button is clicked
    show_board = False  # Used to show board when AI is playing
    stop_game = False  # keeps game board on screen
    winner_button = None
    player_num = 0
    players = [white_player, gray_player]
    current_player = players[0]
    game = current_player.game
    # -------- Main Program Loop -----------
    pygame.event.clear()
    while not game_is_done:
        # --- Main event loop
        SCREEN.fill(LIGHT_GREEN)
        event = pygame.event.poll()  # non-blocking event poll

        # Check all events
        for event in [event] + pygame.event.get():
            if event.type == pygame.QUIT:
                game_is_done = True
            if stop_game and event.type == pygame.MOUSEBUTTONDOWN:
                if winner_button and winner_button.check_press(pygame.mouse.get_pos()):
                    return_to_menu = True
                    game_is_done = True

        ai_player = current_player.player_type != 'human'

        # AI player plays game
        if not stop_game and ai_player:
            current_player, player_num, players, show_board = play_ai_turn(current_player, player_num,
                                                                           players, show_board)

        # Human player plays game
        elif not stop_game and not ai_player:
            current_player, player_num, players = play_human_turn(event, current_player, game, player_num, players)

        # Allow undo during a select action
        if current_player.can_player_undo():
            make_undo_button(current_player)

        # Check for end of game
        if game.end:
            game.end_game(False)
            winner_button = end_fanfare(game.winner if game.winner is not None else game.color)
            stop_game = True

        # Update and redraw winner button on hover
        if stop_game and winner_button:
            winner_button.update(pygame.mouse.get_pos())
            winner_button.draw()

        # Draw player info labels
        draw_player_info(white_player, gray_player)

        # Update the screen
        draw_board(game.board)
        pygame.display.flip()

        # Run at 30 frames per second
        clock.tick(30)

    return return_to_menu


def main():
    """Play game including title screen. Loops back to menu if winner button is clicked."""
    while True:
        player_dict = title_screen()
        this_game = Game()

        white_player = SantoriniPlayer(this_game, player_dict['W'], 'W')
        gray_player = SantoriniPlayer(this_game, player_dict['G'], 'G')

        return_to_menu = play_game(white_player, gray_player)
        if not return_to_menu:
            break


if __name__ == '__main__':
    main()
