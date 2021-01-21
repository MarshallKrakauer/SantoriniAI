# pylint: disable=E1101
"""pygame interaction with Santorini game."""

import pygame
import pygame.freetype
from game import Game
from player import Player
from button import Button

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

def main():
    """Play game including title screen."""
    # Get game board
    player_dict = title_screen()
    this_game = Game()

    white_player = Player(this_game, player_dict['W'], 'W')
    gray_player = Player(this_game, player_dict['G'], 'G')

    play_game(white_player, gray_player)

def map_numbers(x_coor, y_coor):
    """
    Convert coordinates to board spaces.

    Parameters
    ----------
    x_coor : int
        x coordinate of area that was clicked
    y_coor : int
        y coordinate of area that was clicked

    Returns
    -------
    tuple
    area on board that was clicked

    """
    x_1 = (x_coor - BOARD_LEFT_EDGE) // 50
    y_1 = (y_coor - BOARD_TOP_EDGE) // 50
    return (x_1, y_1)

def check_valid(num):
    """Return true if valid board spot."""
    return -1 < num < 5


def end_fanfare(color):
    """Produce visual showing who won the game."""
    pygame.draw.rect(SCREEN, GREEN,
                     BUTTON_MEASURES, 0)
    text = font.render("WINNER: " + color, True, BLACK)
    SCREEN.blit(text, (BUTTON_MEASURES[0] + 20, BUTTON_MEASURES[1] + 20))


def check_undo(x_coor, y_coor):
    """Return true if undo button was selected."""
    return (BOARD_LEFT_EDGE + 75 <= x_coor <= BOARD_LEFT_EDGE + 180
            and BOARD_TOP_EDGE + 350 <= y_coor <= BOARD_TOP_EDGE + 375)


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

def show_thinking(player):
    """Show a "THINKING..." box when AI plays turn."""
    if player.color == 'W':
        button_color = WHITE
    else:
        button_color = GRAY
    undo_button = Button((BUTTON_MEASURES[0] + 50, BUTTON_MEASURES[1] + 20),
                         "THINKING...", 40, button_color, BLUE, 1)
    undo_button.draw()

def draw_board(board):
    """Draw the 5x5 game board with player pieces."""
    for i in range(5):
        for j in range(5):
            V = BOARD_LEFT_EDGE + 50 * i
            H = BOARD_TOP_EDGE + 50 * j
            pygame.draw.rect(SCREEN, WHITE,
                             [V, H, 50, 50], 2)
            # Draw piece or dome

            # Draw occupant
            if board[i][j]['occupant'] == 'X':
                pygame.draw.rect(SCREEN, BLACK,
                                 [V, H, 50, 50], 0)
            elif board[i][j]['occupant'] == 'G':
                pygame.draw.circle(SCREEN, GRAY,
                                   [V + 25, H + 25], 50 / 3)
            elif board[i][j]['occupant'] == 'W':
                pygame.draw.circle(SCREEN, WHITE,
                                   [V + 25, H + 25], 50 / 3)
            # Draw Active space
            if board[i][j]['active']:
                pygame.draw.rect(SCREEN, RED,
                                 [V, H, 50, 50], 3)
            # Draw Winning Space
            if (board[i][j]['level'] == 3
                    and board[i][j]['occupant'] != 'O'):
                pygame.draw.rect(SCREEN, GOLD,
                                 [V, H, 50, 50], 5)

            # Draw height
            text = font.render(str(board[i][j]['level']), True, BLACK)
            SCREEN.blit(text, (V + 20, H + 20))


def draw_arrow(x_coor=0, y_coor=0):
    """Draw arrow onto start screen."""
    pygame.draw.polygon(SCREEN,
                        RED,
                        # Locations to draw
                        ((12 + x_coor, 112 + y_coor),
                         (12 + x_coor, 137 + y_coor),
                            (62 + x_coor, 137 + y_coor),
                            (62 + x_coor, 162 + y_coor),
                            (87 + x_coor, 125 + y_coor),
                            (62 + x_coor, 87 + y_coor),
                            (62 + x_coor, 112 + y_coor)
                         )
                        )


def get_title_screen_buttons():
    """Create title screen buttons."""
    return_dict = {}
    return_dict['start'] = Button(
        center_position=(400, 450),  # left,top
        font_size=75,
        bg_rgb=GREEN,
        text_rgb=BLACK,
        text="CLICK TO START",
        multiplier=1)

    return_dict['white header'] = Button(
        center_position=(200, 100),
        font_size=72,
        bg_rgb=BLUE,
        text_rgb=WHITE,
        text='WHITE',
        multiplier=1)

    return_dict['gray header'] = Button(
        center_position=(600, 100),
        font_size=72,
        bg_rgb=BLUE,
        text_rgb=GRAY,
        text='GRAY',
        multiplier=1.2)

    return_dict['white alphabeta'] = Button(
        center_position=(200, 200),
        font_size=50,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='AI',
        multiplier=1.2)

    return_dict['gray alphabeta'] = Button(
        center_position=(600, 200),
        font_size=50,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='AI',
        multiplier=1.2)

    return_dict['white human'] = Button(
        center_position=(200, 300),
        font_size=50,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='Human',
        multiplier=1.2)

    return_dict['gray human'] = Button(
        center_position=(600, 300),
        font_size=50,
        bg_rgb=BLACK,
        text_rgb=WHITE,
        text='Human',
        multiplier=1.2)

    return return_dict


def title_screen():
    """Show title screen before playing."""
    counter = 0

    button_dict = get_title_screen_buttons()

    (show_white_human_arrow, show_white_ai_arrow, show_gray_human_arrow,
     show_gray_ai_arrow, end_loop) = [False] * 5
    while not end_loop:
        SCREEN.fill(LIGHT_GREEN)

        # Choose where to show red arrow for white piece
        if show_white_human_arrow:
            draw_arrow(30, 200 - 24)
        elif show_white_ai_arrow:
            draw_arrow(30, 100 - 24)

        # Choose where to show red arrow for gray piece
        if show_gray_human_arrow:
            draw_arrow(410, 200 - 24)
        elif show_gray_ai_arrow:
            draw_arrow(410, 100 - 24)

        # Show start button if all choices have been made
        if ((show_gray_human_arrow | show_gray_ai_arrow) and
                (show_white_human_arrow | show_white_ai_arrow) and
                counter % 3000 < 10000):
            button_dict['start'].draw()

        # Draw all four buttons
        for button in button_dict.keys():
            if button != 'start':
                button_dict[button].draw()

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()

            # Check if mouse is hovering over any of the buttons
            for button in button_dict:
                if button not in ['start', 'white header', 'gray header']:
                    button_dict[button].update(pos)

            # Move red arrow based on selection for white
            if (button_dict['white human'].check_press(pos) and
                    event.type == pygame.MOUSEBUTTONDOWN):
                show_white_human_arrow = True
                show_white_ai_arrow = False
            elif (button_dict['white alphabeta'].check_press(pos) and
                  event.type == pygame.MOUSEBUTTONDOWN):
                show_white_human_arrow = False
                show_white_ai_arrow = True

            # Move red arrow based on selection for gray
            if (button_dict['gray human'].check_press(pos) and
                    event.type == pygame.MOUSEBUTTONDOWN):
                show_gray_human_arrow = True
                show_gray_ai_arrow = False
            elif (button_dict['gray alphabeta'].check_press(pos) and
                  event.type == pygame.MOUSEBUTTONDOWN):
                show_gray_human_arrow = False
                show_gray_ai_arrow = True

            # If both choices have been made, show the start button
            if ((show_gray_human_arrow | show_gray_ai_arrow) and
                    (show_white_human_arrow | show_white_ai_arrow)):
                button_dict['start'].update(pos)

            # If person clicks start, star the game!
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_dict['start'].check_press(pos):
                    end_loop = True

            # Allow user to quit the game
            if event.type == pygame.QUIT:
                end_loop = True

        counter += 1
        pygame.display.flip()

    # Choose what to return
    if show_white_human_arrow:
        white_player = 'human'
    else:
        white_player = 'alphabeta'

    if show_gray_human_arrow:
        gray_player = 'human'
    else:
        gray_player = 'alphabeta'

    return {'W': white_player, 'G': gray_player}


def play_game(white_player, gray_player):
    """
    Create and run UI to play Santorini.

    Parameters
    ----------
    game : Game
        Game object where moves/builds will be game
    """
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()
    counter = 0  # not in use, holder if something shows every other frame
    done = False  # ends pygame when true
    show_board = False  # Used to show board when AI is playing
    player_num = 0
    players = [white_player, gray_player]
    current_player = players[0]
    game = current_player.game
    # -------- Main Program Loop -----------
    pygame.event.clear()
    while not done:
        # --- Main event loop
        SCREEN.fill(LIGHT_GREEN)
        event = pygame.event.wait()  # event queue

        # Check if someone clicked x
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        # Special conditions
        # Check for end of game
        if game.end:
            game.end_game(False)
            end_fanfare(current_player.color)  # do something for endgame

        # AI player plays game
        elif current_player.player_type == 'alphabeta':
            show_thinking(current_player)
            if show_board:
                current_player.play_turn()
                show_board = False
            else:
                show_board = True

            if current_player.should_switch_turns():
                player_num = (player_num + 1) % 2
                current_player = players[player_num]
                current_player.update_game()

        # Human player plays game
        elif current_player.player_type == 'human':
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

        # Allow undo during a select action
        if current_player.can_player_undo():
            make_undo_button(current_player)

        # Update the screen
        draw_board(game.board)
        pygame.display.flip()

        # Run at 30 frames per second
        counter += 1
        clock.tick(30)

    # Close the window and quit.
    pygame.quit()

main()
