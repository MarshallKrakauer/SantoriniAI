# pylint: disable=E1101
"""pygame interaction with Santorini game."""

import pygame
from auto_santorini import Game

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
TEST_COLOR = (100, 100, 100)
GOLD = (100, 84.3, 0)
BLUE = (30, 150, 250)

# Horizontal and vertical start of board
START_H = 100
START_V = 100

game1 = Game()
board = game1.board


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
    x_1 = (x_coor - 100) // 50
    y_1 = (y_coor - 100) // 50
    return (x_1, y_1)


def check_valid(num):
    """Return true if valid board spot."""
    return -1 < num < 5


def check_undo(x_coor, y_coor):
    """Return true if undo button was selected."""
    return x_coor >= 175 and x_coor <= 290 and y_coor >= 450 and y_coor <= 500


def end_fanfare(color):
    """Produce visual showing who won the game."""
    pygame.draw.rect(SCREEN, GREEN,
                     [175, 450, 120, 60], 0)
    text = font.render("WINNER: " + color, True, BLACK)
    SCREEN.blit(text, (175 + 20, 450 + 20))


def undo_button():
    """Show undo button when player can select piece."""
    pygame.draw.rect(SCREEN, (50, 50, 50),
                     [175, 450, 120, 60], 0)
    text = font.render("UNDO", True, BLACK)
    SCREEN.blit(text, (175 + 40, 450 + 20))
    pygame.draw.rect(SCREEN, RED,
                     [175, 450, 120, 60], 3)


def show_thinking(dot=3):
    """Show a "THINKING..." box when AI plays turn."""
    elipse = '.' * dot
    pygame.draw.rect(SCREEN, (50, 50, 50),
                     [175, 450, 120, 60], 0)
    text = font.render("THINKING" + elipse, True, BLACK)
    SCREEN.blit(text, (160 + 40, 450 + 20))


def draw_board():
    """Draw the 5x5 game board with player pieces."""
    for i in range(5):
        for j in range(5):
            V = START_V + 50 * i
            H = START_H + 50 * j
            pygame.draw.rect(SCREEN, BLACK,
                             [V, H, 50, 50], 2)
            # Draw piece or dome

            # Draw occupant
            if board[i][j]['occupant'] == 'X':
                pygame.draw.rect(SCREEN, BLACK,
                                 [V, H, 50, 50], 0)
            elif board[i][j]['occupant'] == 'G':
                pygame.draw.circle(SCREEN, TEST_COLOR,
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


# Set up the pygame environment
pygame.init()
SIZE = (450, 600)
SCREEN = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Santorini")
font = pygame.font.SysFont('Calibri', 16, True, False)

# Used to manage how fast the screen updates
clock = pygame.time.Clock()
counter = 0  # not in use, holder if something shows every other frame
done = False  # ends pygame when true
show_board = False  # Used to show board when AI is playing
# -------- Main Program Loop -----------
pygame.event.clear()
while not done:
    # --- Main event loop
    SCREEN.fill(BLUE)

    event = pygame.event.wait()  # event queue
    for event in pygame.event.get():  # check for end of game
        if event.type == pygame.QUIT:
            done = True

    # Special conditions
    # Check for end of game
    if game1.end:
        game1.end_game()
        end_fanfare(game1.color)  # do something for endgame
    # Show that AI is "thinking"
    elif game1.turn > 4 and game1.color == 'G':
        show_thinking()
        if show_board:
            game1.future_moves()
            show_board = False
        else:
            show_board = True
    # Allow undo during a select action
    elif game1.sub_turn == 'move':
        undo_button()

    # Allow player to select actions
    if event.type == pygame.MOUSEBUTTONDOWN and not game1.end:
        pos = pygame.mouse.get_pos()
        x, y = map_numbers(pos[0], pos[1])
        if check_valid(x) and check_valid(y):
            game1.play_turn(x, y)
        elif check_undo(pos[0], pos[1]) and game1.sub_turn == 'move':
            game1.undo()

    # Draw the board after changes have been made
    board = game1.board
    draw_board()

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # --- Limit to 60 frames per second
    counter += 1
    clock.tick(30)

# Close the window and quit.
pygame.quit()
