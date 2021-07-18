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
GRAY = (100, 100, 100)
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
    """Produce visual showing who won the game."""

    pygame.draw.rect(SCREEN, BLUE,
                     BUTTON_MEASURES, 0)
    text = font.render("WINNER: " + color, True, BLACK)
    SCREEN.blit(text, (BUTTON_MEASURES[0] + 20, BUTTON_MEASURES[1] + 20))


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
        center_position=(400, 475),  # left,top
        font_size=75,
        bg_rgb=GREEN,
        text_rgb=BLACK,
        text="CLICK TO START",
        multiplier=1), 'white header': Button(
        center_position=(200, 100),
        font_size=72,
        bg_rgb=BLUE,
        text_rgb=WHITE,
        text='WHITE',
        multiplier=1), 'gray header': Button(
        center_position=(600, 100),
        font_size=72,
        bg_rgb=BLUE,
        text_rgb=GRAY,
        text='GRAY',
        multiplier=1.2), 'white human': Button(
        center_position=(200, 200),
        font_size=40,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='Human',
        multiplier=1.2), 'gray human': Button(
        center_position=(600, 200),
        font_size=40,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='Human',
        multiplier=1.2), 'white minimax': Button(
        center_position=(200, 300),
        font_size=40,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='Minimax',
        multiplier=1.2), 'gray minimax': Button(
        center_position=(600, 300),
        font_size=40,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='Minimax',
        multiplier=1.2), 'white MCTS': Button(
        center_position=(200, 400),
        font_size=40,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='MCTS',
        multiplier=1.2), 'gray MCTS': Button(
        center_position=(600, 400),
        font_size=40,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='MCTS',
        multiplier=1.2)}


def draw_title_screen_material(arrow_dict, button_dict, counter):
    # Choose where to show red arrow for white piece
    if arrow_dict['white minimax']:
        choose_arrow_location(30, 200 - 24)
    elif arrow_dict['white human']:
        choose_arrow_location(30, 100 - 24)
    elif arrow_dict['white MCTS']:
        choose_arrow_location(30, 300 - 24)

    # Choose where to show red arrow for gray piece
    if arrow_dict['gray minimax']:
        choose_arrow_location(410, 200 - 24)
    elif arrow_dict['gray human']:
        choose_arrow_location(410, 100 - 24)
    elif arrow_dict['gray MCTS']:
        choose_arrow_location(410, 300 - 24)

    # Show start button if all choices have been made
    if ((arrow_dict['white human'] | arrow_dict['white minimax'] | arrow_dict['white MCTS']) and
            (arrow_dict['gray human'] | arrow_dict['gray minimax'] | arrow_dict['gray MCTS']) and
            counter % 2500 < 1500):
        button_dict['start'].draw()

    # Draw all four buttons
    for button in button_dict.keys():
        if button != 'start':
            button_dict[button].draw()


def title_screen():
    """Show title screen before playing."""
    counter = 0

    button_dict = get_title_screen_buttons()
    arrow_dict = {'white human': False, 'white minimax': False, 'white MCTS': False,
                  'gray human': False, 'gray minimax': False, 'gray MCTS': False}
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
            if (button_dict['white human'].check_press(pos) and
                    event.type == pygame.MOUSEBUTTONDOWN):
                arrow_dict['white human'] = True
                arrow_dict['white minimax'] = False
                arrow_dict['white MCTS'] = False
            elif (button_dict['white minimax'].check_press(pos) and
                  event.type == pygame.MOUSEBUTTONDOWN):
                arrow_dict['white human'] = False
                arrow_dict['white minimax'] = True
                arrow_dict['white MCTS'] = False
            elif (button_dict['white MCTS'].check_press(pos) and
                  event.type == pygame.MOUSEBUTTONDOWN):
                arrow_dict['white human'] = False
                arrow_dict['white minimax'] = False
                arrow_dict['white MCTS'] = True

            # Move red arrow based on selection for white
            if (button_dict['gray human'].check_press(pos) and
                    event.type == pygame.MOUSEBUTTONDOWN):
                arrow_dict['gray human'] = True
                arrow_dict['gray minimax'] = False
                arrow_dict['gray MCTS'] = False
            elif (button_dict['gray minimax'].check_press(pos) and
                  event.type == pygame.MOUSEBUTTONDOWN):
                arrow_dict['gray human'] = False
                arrow_dict['gray minimax'] = True
                arrow_dict['gray MCTS'] = False
            elif (button_dict['gray MCTS'].check_press(pos) and
                  event.type == pygame.MOUSEBUTTONDOWN):
                arrow_dict['gray human'] = False
                arrow_dict['gray minimax'] = False
                arrow_dict['gray MCTS'] = True

            # If both choices have been made, show the start button
            if ((arrow_dict['white human'] | arrow_dict['white minimax'] | arrow_dict['white MCTS']) and
                    (arrow_dict['gray human'] | arrow_dict['gray minimax'] | arrow_dict['gray MCTS'])):
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
    elif arrow_dict['white MCTS']:
        white_player = 'MCTS'

    if arrow_dict['gray human']:
        gray_player = 'human'
    elif arrow_dict['gray minimax']:
        gray_player = 'alphabeta'
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
    show_board = False  # Used to show board when AI is playing
    stop_game = False  # keeps game board on screen
    player_num = 0
    players = [white_player, gray_player]
    current_player = players[0]
    game = current_player.game
    # -------- Main Program Loop -----------
    pygame.event.clear()
    while not game_is_done:
        # --- Main event loop
        SCREEN.fill(LIGHT_GREEN)
        event = pygame.event.wait()  # event queue

        # Check if someone clicked x
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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
            end_fanfare(game.color)
            stop_game = True

        # Update the screen
        draw_board(game.board)
        pygame.display.flip()

        # Run at 30 frames per second
        clock.tick(30)

    # Close the window and quit.
    pygame.quit()


def main():
    """Play game including title screen."""
    # Get game board
    player_dict = title_screen()
    this_game = Game()

    white_player = SantoriniPlayer(this_game, player_dict['W'], 'W')
    gray_player = SantoriniPlayer(this_game, player_dict['G'], 'G')

    play_game(white_player, gray_player)


if __name__ == '__main__':
    main()
