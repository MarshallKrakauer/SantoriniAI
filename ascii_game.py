"""ASCII/text version of Santorini. Used to reduce overheard associated with Pygame."""

import csv

import pandas as pd

from game import Game
from player import Player


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


def play_game(current_game):
    white_turn = True
    gray_player = Player(game=current_game, color='G', player_type='alphabeta')
    white_player = Player(game=current_game, color='W', player_type='alphabeta')
    while not current_game.end:
        if white_turn:
            white_player.play_turn()
            white_turn = not white_turn
        else:
            gray_player.play_turn()
            white_turn = not white_turn
        print(current_game)
    write_to_game_list(white_player, gray_player)


def main():
    new_game = Game()
    play_game(new_game)


if __name__ == '__main__':
    main()
