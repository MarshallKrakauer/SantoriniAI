"""Gather data from a Santorini Game. Will be used to make predictive model"""

import game
# import pandas as pd
# from time import time
from math import sqrt
import csv
import MCTS

SPACE_LIST = [(i, j) for i in range(5) for j in range(5)]


class SantoriniData:

    def __init__(self, santorini_game, won_game):
        self.win = int(won_game)
        self.data = self.get_board_data(santorini_game)

    def get_board_data(self, santorini_game):
        santorini_game_data = [self.win, santorini_game.turn / 60]
        is_first_our_color = True
        is_first_other_color = True

        our_color_levels_0 = [0, 0, 0]
        our_color_levels_1 = [0, 0, 0]
        other_color_levels_0 = [0, 0, 0]
        other_color_levels_1 = [0, 0, 0]
        player_space_li = []
        other_space_li = []

        for i, j in SPACE_LIST:
            if santorini_game.board[i][j]['occupant'] == santorini_game.color:
                player_space_li.append((i, j))
                if is_first_our_color:
                    our_color_levels_0[santorini_game.board[i][j]['level']] += 1
                    our_color_levels_0.extend(self.get_adjacent(i, j, santorini_game))
                    is_first_our_color = False
                else:
                    our_color_levels_1[santorini_game.board[i][j]['level']] += 1
                    our_color_levels_1.extend(self.get_adjacent(i, j, santorini_game))

            elif santorini_game.board[i][j]['occupant'] == santorini_game.opponent_color:
                other_space_li.append((i, j))
                if is_first_other_color:
                    other_color_levels_0[santorini_game.board[i][j]['level']] += 1
                    other_color_levels_0.extend(self.get_adjacent(i, j, santorini_game))
                    is_first_other_color = False
                else:
                    other_color_levels_1[santorini_game.board[i][j]['level']] += 1
                    other_color_levels_1.extend(self.get_adjacent(i, j, santorini_game))

        player_col_0, player_row_0 = player_space_li[0]
        player_col_1, player_row_1 = player_space_li[1]

        opponent_col_0, opponent_row_0 = other_space_li[0]
        opponent_col_1, opponent_row_1 = other_space_li[1]

        opponent_distance = [distance_between(player_col_0, player_row_0, opponent_col_0, opponent_row_0) / sqrt(32),
                             distance_between(player_col_0, player_row_0, opponent_col_1, opponent_row_1) / sqrt(32),
                             distance_between(player_col_1, player_row_1, opponent_col_1, opponent_row_1) / sqrt(32),
                             distance_between(player_col_1, player_row_1, opponent_col_0, opponent_row_0) / sqrt(32)]
        opponent_distance.sort()
        self_distance = distance_between(player_col_0, player_row_0, player_col_1, player_row_0) / sqrt(32)

        # Add other lists to final list
        santorini_game_data.extend(our_color_levels_0)
        santorini_game_data.extend(our_color_levels_1)
        santorini_game_data.extend(other_color_levels_0)
        santorini_game_data.extend(other_color_levels_1)
        santorini_game_data.extend(opponent_distance)
        santorini_game_data.append(self_distance)

        return santorini_game_data

    @staticmethod
    def get_board_data_convolutional(santorini_game):
        list_of_lists = []
        player_list = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
        opponent_list = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
        height_list = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
        for i, j in SPACE_LIST:
            height_list[i][j] = santorini_game.board[i][j]['level']

            if santorini_game.board[i][j]['occupant'] == santorini_game.color:
                player_list[i][j] = 1
            elif santorini_game.board[i][j]['occupant'] == santorini_game.opponent_color:
                opponent_list[i][j] = 1

        list_of_lists.extend([player_list, opponent_list, height_list])

        return list_of_lists

    @staticmethod
    def get_adjacent(x_val, y_val, santorini_game):
        """
        Get spaces surrounding the passed one.
        Parameters
        ----------
        x_val : int
             ie column value
        y_val : int
            ie row value
        santorini_game: Game
            Game to extract board from and find height of surrounding spaces
        Returns
        -------
        space_li : li
            list of spaces adjacent to the one provided through
            x_val and y_val
        """
        height_list = [0, 0, 0, 0, 0]

        adj_space_list = [(x_val - 1, y_val + 1),
                          (x_val, y_val + 1),
                          (x_val + 1, y_val + 1),
                          (x_val - 1, y_val),
                          (x_val + 1, y_val),
                          (x_val - 1, y_val - 1),
                          (x_val, y_val - 1),
                          (x_val + 1, y_val - 1)]

        for i, j in adj_space_list:
            if 0 <= i <= 4 and 0 <= j <= 4:
                height_list[santorini_game.board[i][j]['level']] += 1 / 8
            else:
                height_list[4] += 1 / 8

        return height_list

    @staticmethod
    def make_columns():
        """Return column names for game data"""
        return """win, turn, 
                self_height_0_0, self_height_0_1, self_height_0_2, num_adj_0_0,
                num_adj_0_1, num_adj_0_2, num_adj_0_3, num_adj_0_X,
                self_height_1_0, self_height_1_1, self_height_1_2, num_adj_1_0,
                num_adj_1_1, num_adj_1_2, num_adj_1_3, num_adj_1_X,
                opponent_height_0_0, opponent_height_0_1, opponent_height_0_2,
                num_adj_0_0, num_adj_0_1, num_adj_0_2, num_adj_0_3, num_adj_0_X,
                opponent_height_1_0, opponent_height_1_1, opponent_height_1_2,
                num_adj_1_0, num_adj_1_1, num_adj_1_2, num_adj_1_3, num_adj_1_X,
                dist_0, dist_1, dist_2, dist_3, self_distance"""


def distance_between(col_0, row_0, col_1, row_1):
    """Geometrics distance between two points"""
    return sqrt((col_0 - col_1) ** 2 + (row_0 - row_1) ** 2)


def append_list_as_row(file_name, list_of_elem):
    """
    Add list of values to CSV file.

    """

    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = csv.writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)


def setup_game():
    init_game = game.Game()
    init_game.randomize_placement('W')
    init_game.randomize_placement('G')
    init_game = init_game.game_deep_copy(init_game, 'W')
    return init_game


def create_game_data(new_game):
    return_li = []

    while not new_game.end:
        mcts_game_tree = MCTS.TreeSearch(new_game)
        mcts_game_tree.search_tree(15)
        best_node = mcts_game_tree.get_best_move()
        new_game.board = best_node.game.board
        new_game.end = best_node.game.end
        new_game.winner = best_node.game.winner

        if not new_game.end:
            new_game.turn = best_node.game.turn
        else:
            new_game.turn = best_node.game.turn + 1

        if not new_game.end:
            return_li.append(new_game.game_deep_copy(new_game, new_game.color))

    return return_li, new_game


def send_game_data_to_csv(game_list, final_move):
    game_winner = final_move.winner
    for idx, elem in enumerate(game_list):
        if elem.winner is None:
            if idx % 2 == 0:
                color = 'W'
            else:
                color = 'G'
            win = color == game_winner
            santorini_data = SantoriniData(elem, win).data
            append_list_as_row('game_list.csv', santorini_data)
            print(idx, ':\n', elem, '\n', santorini_data)


if __name__ == '__main__':
    for i in range(10):
        train_game = setup_game()
        new_game_list, final_game = create_game_data(train_game)
        winner = final_game.winner
        send_game_data_to_csv(new_game_list, final_game)
