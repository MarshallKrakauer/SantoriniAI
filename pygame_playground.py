# pylint: disable=E1101
"""pygame interaction with Santorini game."""

import pygame
import pygame.freetype
from auto_santorini import Game

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
TEST_COLOR = (100, 100, 100)
GOLD = (100, 84.3, 0)
BLUE = (30, 250, 150)

# Horizontal and vertical start of board
BOARD_TOP_EDGE = 100 # SIZE = (800, 600) #(width <-->, height)
BOARD_LEFT_EDGE = 275
BUTTON_MEASURES = [BOARD_LEFT_EDGE + 75, BOARD_TOP_EDGE + 350, 120, 60]
# Left_edge, top_edge, width, height

# Set up the pygame environment
pygame.init()
SIZE = (800, 600) #(width <-->, height)
SCREEN = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Santorini")
font = pygame.font.SysFont('Calibri', 16, True, False)

class Button(pygame.sprite.Sprite):
    # Curtosy of https://programmingpixels.com/handling-a-title-screen-game-flow-and-buttons-in-pygame.html
    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb):
        self.mouse_over = False  # indicates if the mouse is over the element
         # default image
        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb)

        # image when hovering over
        highlighted_image = create_surface_with_text(
            text=text,
            font_size=font_size * 1.2, text_rgb=text_rgb, bg_rgb=bg_rgb)

        self.images = [default_image, highlighted_image]

        self.rectangles = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position),
        ]

        # Calls init on parent class
        super().__init__()

    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rectangles[1] if self.mouse_over else self.rectangles[0]

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
        else:
            self.mouse_over = False
    
    def draw(self):
        """ Draws element onto a surface."""
        SCREEN.blit(self.image, self.rect)

def create_surface_with_text(text, font_size, text_rgb, bg_rgb):
    """ Returns surface with text written on """
    font = pygame.freetype.SysFont("Courier", font_size, bold=True)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()

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

def check_undo(x_coor, y_coor):
    """Return true if undo button was selected."""
    return (BOARD_LEFT_EDGE + 75 <= x_coor <= BOARD_LEFT_EDGE + 190
            and BOARD_TOP_EDGE + 350 <= y_coor <= BOARD_TOP_EDGE + 400)


def end_fanfare(color):
    """Produce visual showing who won the game."""
    pygame.draw.rect(SCREEN, GREEN,
                     BUTTON_MEASURES, 0)
    text = font.render("WINNER: " + color, True, BLACK)
    SCREEN.blit(text, (175 + 20, 450 + 20))

def undo_button():
    """Show undo button when player can select piece."""
    x, y = pygame.mouse.get_pos()
    if check_undo(x,y):
        undo_font = pygame.font.SysFont('Calibri', 24, True, False)
        #pygame.draw.rect(SCREEN, (50, 50, 50),
        #             BUTTON_MEASURES, 0)
        text = undo_font.render("UNDO", True, BLACK)
        SCREEN.blit(text, (BUTTON_MEASURES[0] + 45/2, BUTTON_MEASURES[1] + 20))
    else:
        undo_font = pygame.font.SysFont('Calibri', 12, True, False)
        #pygame.draw.rect(SCREEN, (50, 50, 150),
        #             BUTTON_MEASURES, 0)
        text = undo_font.render("UNDO", True, BLACK)
        SCREEN.blit(text, (BUTTON_MEASURES[0] + 45, BUTTON_MEASURES[1] + 20))
    
    #pygame.draw.rect(SCREEN, RED,BUTTON_MEASURES, 3)

def show_thinking(dot=3):
    """Show a "THINKING..." box when AI plays turn."""
    elipse = '.' * dot
    pygame.draw.rect(SCREEN, (50, 50, 50),
                     BUTTON_MEASURES, 0)
    text = font.render("THINKING" + elipse, True, BLACK)
    SCREEN.blit(text, (BUTTON_MEASURES[0] + 20, BUTTON_MEASURES[1] + 20))

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


def title_screen():
    """Show title screen before playing."""
    
    start_button = Button(
        center_position=(200,200),
        font_size=20,
        bg_rgb=BLUE,
        text_rgb=WHITE,
        text="Hello World",
    )
    
    end_it = False
    myname = "Santorini"
    while end_it==False:
        SCREEN.fill(WHITE)
        myfont=pygame.font.SysFont("Britannic Bold", 40)
        nlabel=myfont.render("Welcome "+myname+" Start Screen", 1, (255, 0, 0))
        start_button.update(pygame.mouse.get_pos())
        start_button.draw()
        
        for event in pygame.event.get():
            if event.type== pygame.MOUSEBUTTONDOWN:
                end_it=True
        SCREEN.blit(nlabel,(800/2,400/2))
        pygame.display.flip()

def title_alt():
    pass
    

def play_game(game):
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
        if game.end:
            game.end_game()
            end_fanfare(game.color)  # do something for endgame
        # Show that AI is "thinking"
        elif game.turn > 4 and game.color == 'G':
            show_thinking()
            if show_board:
                game.future_moves()
                show_board = False
            else:
                show_board = True
        # Allow undo during a select action
        elif game.sub_turn == 'move':
            undo_button()

        # Allow player to select actions
        if event.type == pygame.MOUSEBUTTONDOWN and not game.end:
            pos = pygame.mouse.get_pos()
            print(pos)
            x, y = map_numbers(pos[0], pos[1])
            if check_valid(x) and check_valid(y):
                game.play_turn(x, y)
            elif check_undo(pos[0], pos[1]) and game.sub_turn == 'move':
                game.undo()

        # Draw the board after changes have been made
        board = game.board
        draw_board(board)

        # --- Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        # --- Limit to 60 frames per second
        counter += 1
        clock.tick(30)

    # Close the window and quit.
    pygame.quit()

pygame.init()
SIZE = (800, 600) #(width <-->, height)
SCREEN = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Santorini")

def main():
    """Play game including title screen."""
    # Get game board
    game1 = Game()
    title_screen()
    play_game(game1)

main()