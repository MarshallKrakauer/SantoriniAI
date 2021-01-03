import pygame
from auto_santorini import Game

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
TEST_COLOR = (100,100,100)
GOLD = (100, 84.3, 0)
BLUE = (30 ,150 ,250)

START_H = 100
START_V = 100

#font = pygame.font.SysFont('Calibri', 16, True, False)

game1 = Game()
board = game1.get_board()
print(type(board))

def map_numbers(x,y):
    x_1 = (x - 100) // 50
    y_1 = (y - 100) // 50
    return((x_1,y_1)) 

def check_valid(num):
    return num > -1 and num < 5

def check_undo(x, y):
    return x >= 175 and x <= 290 and y >= 450 and y <= 500

def end_fanfare(color):
    pygame.draw.rect(screen,GREEN,
                             [175,450,120,60],0)
    text = font.render("WINNER: " + color,True,BLACK)
    screen.blit(text,(175 + 20,450 + 20))
    
def undo_button():
    pygame.draw.rect(screen,(50,50,50),
                             [175,450,120,60],0)
    text = font.render("UNDO",True,BLACK)
    screen.blit(text,(175 + 40,450 + 20))
    pygame.draw.rect(screen,RED,
                             [175,450,120,60],3)

def show_thinking(dot = 3):
    elipse = '.' * dot
    pygame.draw.rect(screen,(50,50,50),
                             [175,450,120,60],0)
    text = font.render("THINKING" + elipse,True,BLACK)
    screen.blit(text,(160 + 40,450 + 20))

def draw_board():
    for i in range(5):
        for j in range(5):
            V = START_V + 50 * i
            H = START_H + 50 * j
            pygame.draw.rect(screen,BLACK,
                             [V,H,50,50],2)
            # Draw piece or dome
            
            #Draw occupant
            if(board[i][j]['occupant'] == 'X'):
                pygame.draw.rect(screen,BLACK,
                             [V,H,50,50],0)
            elif(board[i][j]['occupant'] == 'G'):
                pygame.draw.circle(screen,TEST_COLOR,
                             [V + 25,H + 25]
                             ,50/3)
            elif(board[i][j]['occupant'] == 'W'):
                pygame.draw.circle(screen,WHITE,
                             [V + 25,H + 25]
                             ,50/3)
            #Draw Active space
            if board[i][j]['active'] == True:
                pygame.draw.rect(screen,RED,
                             [V,H,50,50],3)
            #Draw Winning Space
            if (board[i][j]['level'] == 3 
                and board[i][j]['occupant'] != 'O'):
                pygame.draw.rect(screen,GOLD,
                             [V,H,50,50],5)
            
            # Draw height
            text = font.render(str(board[i][j]['level']),True,BLACK)
            screen.blit(text,(V + 20,H + 20))
            
pygame.init()
font = pygame.font.SysFont('Calibri', 16, True, False)
 
# Set the width and height of the screen [width, height]
size = (450, 600)
screen = pygame.display.set_mode(size)
 
pygame.display.set_caption("Santorini")
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()

turn = 0
counter = 0
done = False
show_board = False
# -------- Main Program Loop -----------
pygame.event.clear()
while not done:
    # --- Main event loop
    
    event = pygame.event.wait()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
 
    # --- Screen-clearing code goes here
    
    # Here, we clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
 
    # If you want a background image, replace this clear with blit'ing the
    # background image.
    screen.fill(BLUE)

    # Visuals to show on screen 
    
    
    
    if game1.end:
        game1.end_game()
        end_fanfare(game1.get_color()) #do something for endgame
    # Show that AI is "thinking"

    elif game1.turn > 4 and game1.color == 'G':
        show_thinking()
        if show_board:
            game1.future_moves()
            show_board = False
        else:
            show_board = True
    # Let player undo action
            
    elif game1.sub_turn == 'move':
        undo_button()  


    if event.type == pygame.MOUSEBUTTONDOWN and not game1.end:
        pos = pygame.mouse.get_pos()
        x, y = map_numbers(pos[0], pos[1])
        if check_valid(x) and check_valid(y):
            game1.play_turn(x, y)
        elif check_undo(pos[0], pos[1]) and game1.sub_turn == 'move':
            game1.undo()    
    
    board = game1._board
    draw_board()

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # --- Limit to 60 frames per second
    counter += 1
    clock.tick(30)
 
# Close the window and quit.
pygame.quit()