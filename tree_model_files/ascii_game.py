"""ASCII/text version of Santorini. Used to reduce overheard associated with Pygame.

Player interface is minimal. It is not meant to replace full UI of the pygame GUI. Just meant
to be playable by those without access to pygame
"""

import csv
import sys

import pandas as pd

import game
import santorini_player

LOG_INFO = False


def write_to_game_list(white_player, gray_player):
    """
    Create list to append to "game_list.csv" list. This will track whether a given player was a human or
    AI. In the future, additional types of AIs will be included. For now, it is either human or alphabeta

    Attributes
    ----------
    white_player : Player
        Player object for the W color
    gray_player : Player
        Player object for the G color
    """
    df = pd.read_csv('game_list.csv')
    next_id = df['id'].max() + 1
    csv_row = [next_id, white_player.player_type, gray_player.player_type]
    with open(r'game_list.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csv_row)


def get_player_type(white_player=True):
    """
    Have user enter the player type.

    Attributes
    ----------
    white_player: bool
        True if entry is for white player, False for gray
    """
    # Entry Prompt
    if white_player:
        user_entry = input("W player type: (H)uman/(Mi)nimax/(MC)TS: ")
    else:
        user_entry = input("G player type: (H)uman/(Mi)nimax/(MC)TS: ")

    # Get entry from user
    if user_entry == 'H':
        return 'human'
    elif user_entry == 'Mi':
        return 'alphabeta'
    elif user_entry == 'MC':
        return 'MCTS'
    else:
        print("Please enter H, Mi, or MC")
        get_player_type(white_player)


def get_coordinates(sub_turn):
    """
    Obtain coordinates entered by human user

    Attributes
    ----------
    sub_turn: str
        Game's sub turn. Used to prompt user.
    """
    print(sub_turn, 'phase')
    user_input = input("Please input in following format: xy ")
    column, row = -1, -1  # Adding this in in case other issues aren't caught
    if len(user_input) != 2:
        print("Please enter two digits")
        return -1, -1
    try:
        column = int(user_input[0])
        row = int(user_input[1])

        if column > 4 or row > 4:
            print("Please enter numbers between 0 and 4 (inclusive)")
            column, row = -1, -1

    except TypeError:
        print("Invalid entry. Example of valid entry: 03")
        column, row = -1, -1
    except ValueError as v:
        column, row = -1, -1
        print(v)
    finally:
        return column, row


def play_game(current_game, print_boards=True):
    """Obtains player type for both players and plays both games."""
    white_player_type = get_player_type()
    gray_player_type = get_player_type(False)
    white_turn = True
    gray_player = santorini_player.SantoriniPlayer(game=current_game, color='G', player_type=gray_player_type)
    white_player = santorini_player.SantoriniPlayer(game=current_game, color='W', player_type=white_player_type)
    while not current_game.end:
        print(current_game)
        if white_turn:
            print("~~~WHITE TURN~~~")
            if white_player.player_type == 'human':
                column, row = get_coordinates(current_game.sub_turn)
                if column != -1:  # -1 indicates a mis-entry
                    white_player.play_turn(column, row)
                # On a successful turn, switch to the next player
                if white_player.should_switch_turns():
                    white_player.update_game()
                    white_turn = not white_turn
            else:
                white_player.play_turn()
                white_player.update_game()
                white_turn = not white_turn
        else:
            print("~~~GRAY TURN~~~")
            if gray_player.player_type == 'human':
                column, row = get_coordinates(current_game.sub_turn)
                if column != -1:  # -1 indicates a mis-entry
                    gray_player.play_turn(column, row)
                gray_player.play_turn(column, row)

                # On a successful turn, switch to the next player
                if gray_player.should_switch_turns():
                    gray_player.update_game()
                    white_turn = not white_turn
            else:
                gray_player.play_turn()
                gray_player.update_game()
                white_turn = not white_turn

        if print_boards:
            print(current_game)
    write_to_game_list(white_player, gray_player)
    print("This game's winner is...", current_game.color)


def main():
    if LOG_INFO:
        old_stdout = sys.stdout
        logfile = open("endgame_testing.log", 'w')
        sys.stdout = logfile
        new_game = game.Game()
        play_game(new_game, True)
        sys.stdout = old_stdout
        logfile.close()
    else:
        new_game = game.Game()
        play_game(new_game, True)


if __name__ == '__main__':
    main()
