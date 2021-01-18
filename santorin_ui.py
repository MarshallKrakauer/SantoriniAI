# pylint: disable=E1101
"""pygame interaction with Santorini game."""

import pygame
import pygame.freetype
from game import Game
from player import Player

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GRAY  = (100, 100, 100)
GOLD  = (100, 84.3, 0)
LIGHT_GREEN = (30, 250, 150)

# Horizontal and vertical start of board
BOARD_TOP_EDGE = 100 # SIZE = (800, 600) #(width <-->, height)
BOARD_LEFT_EDGE = 275
BUTTON_MEASURES = [BOARD_LEFT_EDGE + 75, BOARD_TOP_EDGE + 350, 120, 60]
                # Left_edge,             top_edge,             width, height

# Set up the pygame environment
pygame.init()
SIZE = (800, 600) #(width <-->, height)
SCREEN = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Santorini")
font = pygame.font.SysFont('Calibri', 16, True, False)

class Button(pygame.sprite.Sprite):
    """
    Button that grows in size when hovered over.

    Helps from: https://programmingpixels.com/handling-a-title-
                screen-game-flow-and-buttons-in-pygame.html
    Attributes

    mouse_over : bool
        Ture if a mouse is hovering over. used to make button larger
    images : list
        list of words that button will show
    rectangles : list
        list of background rectangles for words    
    multiplier: float
        how much image increases when its moused over.
        multipler of 1 makes a static image
    """
    
    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb,
                 multiplier = 1.2):

        self.mouse_over = False  # indicates if the mouse is over the element
         # default image
        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb)

        # image when hovering over
        highlighted_image = create_surface_with_text(
            text=text,
            font_size=font_size * multiplier, text_rgb=text_rgb, bg_rgb=bg_rgb)

        self.images = [default_image, highlighted_image]

        self.rectangles = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position),
        ]

        # Calls init on parent class
        super().__init__()

    @property
    def image(self):
        """
        Change between small and large button.

        Returns
        -------
        pygame image
            larger or smaller version of button
        """
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        """
        Change between small and large button.
        
        Sister function of image

        Returns
        -------
        pygame image
            larger or smaller version of button
        """
        return self.rectangles[1] if self.mouse_over else self.rectangles[0]

    def update(self, mouse_pos):
        """
        Change value of mouse_over, which is used for draw and check_press.

        Parameters
        ----------
        mouse_pos : tuple
            (x,y) coordinates of position
        """
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
        else:
            self.mouse_over = False
    
    def check_press(self, mouse_pos):
        """Check if user pressed the button."""
        return self.rect.collidepoint(mouse_pos)
    
    def draw(self):
        """Draws element onto a surface."""
        SCREEN.blit(self.image, self.rect)

def create_surface_with_text(text, font_size, text_rgb, bg_rgb):
    """Return surface with text written on."""
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

def end_fanfare(color):
    """Produce visual showing who won the game."""
    pygame.draw.rect(SCREEN, GREEN,
                     BUTTON_MEASURES, 0)
    text = font.render("WINNER: " + color, True, BLACK)
    SCREEN.blit(text, (175 + 20, 450 + 20))

def check_undo(x_coor, y_coor):
    """Return true if undo button was selected."""
    return (BOARD_LEFT_EDGE + 75 <= x_coor <= BOARD_LEFT_EDGE + 180
            and BOARD_TOP_EDGE + 350 <= y_coor <= BOARD_TOP_EDGE + 375)

def make_undo_button():
    """Show undo button and allow user to choose it."""
    undo_button = Button((BUTTON_MEASURES[0] + 50, BUTTON_MEASURES[1] + 20),
                         "UNDO", 30, GRAY, BLACK, 1.5)
    undo_button.update(pygame.mouse.get_pos())
    undo_button.draw()

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

def draw_arrow(x_coor = 0, y_coor = 0):
    """Draw arrow onto start screen."""
    pygame.draw.polygon(SCREEN, 
                    RED,
                    # Locations to draw
                    ((12 + x_coor, 112 + y_coor), 
                     (12 + x_coor, 137 + y_coor), 
                     (62 + x_coor, 137 + y_coor), 
                     (62 + x_coor, 162 + y_coor), 
                     (87 + x_coor, 125   + y_coor), 
                     (62 + x_coor, 87  + y_coor), 
                     (62 + x_coor, 112 + y_coor)
                     )
                    )

def title_screen():
    """Show title screen before playing."""
    counter = 0
    
    start_button = Button(
        center_position=(400, 450), #left,top
        font_size=75,
        bg_rgb=GREEN,
        text_rgb=BLACK,
        text="CLICK TO START",
        multiplier = 1)

    white_header = Button(
        center_position= (200,100),
        font_size = 72,
        bg_rgb = BLUE,
        text_rgb = WHITE,
        text = 'WHITE',
        multiplier = 1)
    
    ai_button_white = Button(
        center_position= (200,200),
        font_size = 50,
        bg_rgb = BLACK,
        text_rgb = WHITE,
        text = 'AI',
        multiplier = 1.2)
    
    ai_button_gray = Button(
        center_position= (600,200),
        font_size = 50,
        bg_rgb = BLACK,
        text_rgb = WHITE,
        text = 'AI',
        multiplier = 1.2)
    
    human_button_white = Button(
        center_position= (200,300),
        font_size = 50,
        bg_rgb = BLACK,
        text_rgb = WHITE,
        text = 'Human',
        multiplier = 1.2)
    
    human_button_gray = Button(
        center_position= (600,300),
        font_size = 50,
        bg_rgb = BLACK,
        text_rgb = WHITE,
        text = 'Human',
        multiplier = 1.2)
    
    grey_header = Button(
        center_position= (600,100),
        font_size = 72,
        bg_rgb = BLUE,
        text_rgb = GRAY,
        text = 'GRAY',
        multiplier = 1.2)

    (show_white_human_arrow, show_white_ai_arrow, show_gray_human_arrow, 
    show_gray_ai_arrow, end_loop) = [False] * 5
    while not end_loop:
        SCREEN.fill(LIGHT_GREEN)
        
        # Choose where to show red arrow for white piece
        if show_white_human_arrow:
            draw_arrow(30,200 - 24)
        elif show_white_ai_arrow:
            draw_arrow(30,100 - 24)
        
        # Choose where to show red arrow for gray piece
        if show_gray_human_arrow:
            draw_arrow(410,200 - 24)
        elif show_gray_ai_arrow:
            draw_arrow(410,100 - 24)
        
        if ((show_gray_human_arrow | show_gray_ai_arrow ) and
                (show_white_human_arrow | show_white_ai_arrow ) and
                counter % 3000 < 2000):
            start_button.draw()
            
        # Draw all four buttons
        ai_button_white.draw()
        human_button_white.draw()            
        ai_button_gray.draw()
        human_button_gray.draw()
        
        # Draw the two headers
        white_header.draw()
        grey_header.draw()

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            
            # Check if mouse is hovering over any of the buttons
            ai_button_white.update(pos)
            human_button_white.update(pos)
            ai_button_gray.update(pos)
            human_button_gray.update(pos)
            
            # Move red arrow based on selection for white
            if (human_button_white.check_press(pos) and
                event.type == pygame.MOUSEBUTTONDOWN):
                show_white_human_arrow = True
                show_white_ai_arrow = False
            elif (ai_button_white.check_press(pos) and
                event.type == pygame.MOUSEBUTTONDOWN):
                show_white_human_arrow = False
                show_white_ai_arrow = True
            
            # Move red arrow based on selection for gray
            if (human_button_gray.check_press(pos) and
                event.type == pygame.MOUSEBUTTONDOWN):
                show_gray_human_arrow = True
                show_gray_ai_arrow = False
            elif (ai_button_gray.check_press(pos) and
                event.type == pygame.MOUSEBUTTONDOWN):
                show_gray_human_arrow = False
                show_gray_ai_arrow = True
            
            # If both choices have been made, show the start button
            if ((show_gray_human_arrow | show_gray_ai_arrow ) and
                (show_white_human_arrow | show_white_ai_arrow )):
                start_button.update(pos)
            
            # If person clicks start, star the game!
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.check_press(pos):
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
    
    return {'W' : white_player, 'G': gray_player}

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
            game.end_game()
            end_fanfare(current_player.color)  # do something for endgame
        # Show that AI is "thinking"
        elif current_player.player_type == 'alphabeta':
            show_thinking()
            if show_board:
                current_player.play_turn()
                show_board = False
            else:
                show_board = True
        elif current_player.player_type == 'human':
            if event.type == pygame.MOUSEBUTTONDOWN and not game.end:
                pos = pygame.mouse.get_pos()
                x, y = map_numbers(pos[0], pos[1])
                if check_valid(x) and check_valid(y):
                    current_player.play_turn(x, y)                         
                if check_undo(pos[0], pos[1]) and game.sub_turn == 'move':
                    game.undo()
        
        if game.sub_turn == 'switch':
            print('hello')
            import time
            time.sleep(3)
            player_num = (player_num + 1) % 2
            current_player = players[player_num]
            current_player.game.color = current_player.color
            print(player_num)
            print(current_player)
        
            if current_player.placements >= 2:
                game.sub_turn = 'select'
            else:
                game.sub_turn = 'place'
        
        
        # Allow undo during a select action
        if current_player.player_type == 'human' and game.sub_turn == 'move':
            make_undo_button()
        '''
        elif current_player.player_type == 'human' and game.sub_turn == 'move':
            pass
        '''
        
        # Draw the board after changes have been made
        #print(game)
        draw_board(game.board)
        # --- Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        # --- Limit to 60 frames per second
        counter += 1
        clock.tick(30)

    # Close the window and quit.
    pygame.quit()

def main():
    """Play game including title screen."""
    # Get game board
    player_dict = title_screen()
    this_game = Game()
    
    white_player = Player(this_game, player_dict['W'], 'W')
    gray_player = Player(this_game, player_dict['G'], 'G')
    
    
    play_game(white_player, gray_player)

main()