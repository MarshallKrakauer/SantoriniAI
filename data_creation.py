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
        santorini_game_data = [self.win, santorini_game.turn]
        our_color_levels = []
        other_color_levels = []

        player_space_li = []
        other_space_li = []

        for i, j in SPACE_LIST:
            if santorini_game.board[i][j]['occupant'] == santorini_game.color:
                our_color_levels.append(santorini_game.board[i][j]['level'])
                player_space_li.append((i, j))
                adj = self.get_adjacent(i, j, santorini_game)
                adj.sort()
                our_color_levels.extend(adj)
            elif santorini_game.board[i][j]['occupant'] == santorini_game.opponent_color:
                other_color_levels.append(santorini_game.board[i][j]['level'])
                other_space_li.append((i, j))
                adj = self.get_adjacent(i, j, santorini_game)
                adj.sort()
                other_color_levels.extend(adj)

        player_col_0, player_row_0 = player_space_li[0]
        player_col_1, player_row_1 = player_space_li[1]

        opponent_col_0, opponent_row_0 = other_space_li[0]
        opponent_col_1, opponent_row_1 = other_space_li[1]

        opponent_distance = [distance_between(player_col_0, player_row_0, opponent_col_0, opponent_row_0),
                             distance_between(player_col_0, player_row_0, opponent_col_1, opponent_row_1),
                             distance_between(player_col_1, player_row_1, opponent_col_1, opponent_row_1),
                             distance_between(player_col_1, player_row_1, opponent_col_0, opponent_row_0)]
        opponent_distance.sort()
        self_distance = distance_between(player_col_0, player_row_0, player_col_1, player_row_0)

        our_color_levels = self.worker_level_sort(our_color_levels)
        other_color_levels = self.worker_level_sort(other_color_levels)
        our_color_levels.extend(other_color_levels)

        for x in our_color_levels:
            santorini_game_data.extend(self.make_list(x))

        santorini_game_data.extend(opponent_distance)
        santorini_game_data.append(self_distance)

        return santorini_game_data

    @staticmethod
    def worker_level_sort(worker_list):
        if worker_list[0] > worker_list[9]:
            temp = worker_list[0:9]
            worker_list[0:9] = worker_list[9:18]
            worker_list[9:18] = temp

        return worker_list

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
        height_list = []

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
                height_list.append(santorini_game.board[i][j]['level'])
            else:
                height_list.append(4)

        return height_list

    @staticmethod
    def make_columns():
        col_list = []

        self_cols = ['self_0', 'self_0_adj_0', 'self_0_adj_1', 'self_0_adj_2', 'self_0_adj_3',
                     'self_0_adj_4', 'self_0_adj_5', 'self_0_adj_6', 'self_0_adj_7',
                     'self_1', 'self_1_adj_0', 'self_1_adj_1', 'self_1_adj_2', 'self_1_adj_3',
                     'self_1_adj_4', 'self_1_adj_5', 'self_1_adj_6', 'self_1_adj_7',
                     ]

        opp_cols = ['opp_0', 'opp_0_adj_0', 'opp_0_adj_1', 'opp_0_adj_2', 'opp_0_adj_3',
                    'opp_0_adj_4', 'opp_0_adj_5', 'opp_0_adj_6', 'opp_0_adj_7',
                    'opp_1', 'opp_1_adj_0', 'opp_1_adj_1', 'opp_1_adj_2', 'opp_1_adj_3',
                    'opp_1_adj_4', 'opp_1_adj_5', 'opp_1_adj_6', 'opp_1_adj_7',
                    ]

        self_cols.extend(opp_cols)

        for col in self_cols:
            for num in [0, 1, 2, 3, 4]:
                col_list.append(col + '_' + str(num))

        return col_list

    @staticmethod
    def make_list(worker_level):
        return_list = [0, 0, 0, 0, 0]
        return_list[worker_level] = 1
        return return_list


def distance_between(col_0, row_0, col_1, row_1):
    """Geometrics distance between two points"""
    return sqrt((col_0 - col_1) ** 2 + (row_0 - row_1) ** 2)


# <editor-fold desc="Creating test game">
train_game = game.Game()
train_game.color = 'W'
train_game.turn = 10
train_game.board[2][0]['occupant'] = 'G'
train_game.board[2][2]['level'] = 2
train_game.board[2][1]['level'] = 0
train_game.board[0][3]['occupant'] = 'G'
train_game.board[1][3]['level'] = 1

train_game.board[2][2]['occupant'] = 'W'
train_game.board[2][2]['level'] = 2
train_game.board[3][3]['level'] = 0
train_game.board[4][4]['occupant'] = 'W'
train_game.board[4][4]['level'] = 1


# </editor-fold>


def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = csv.writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)


def setup_game():
    train_game = game.Game()
    train_game.randomize_placement('W')
    train_game.randomize_placement('G')
    train_game = train_game.game_deep_copy(train_game, 'W')
    return train_game


def create_game_data(train_game):
    while not train_game.end:
        mcts_game_tree = MCTS.TreeSearch(train_game)
        mcts_game_tree.search_tree(15)
        best_node = mcts_game_tree.get_best_move()
        train_game.board = best_node.game.board
        train_game.end = best_node.game.end
        train_game.winner = best_node.game.winner

        if not train_game.end:
            train_game.turn = best_node.game.turn
        else:
            train_game.turn = best_node.game.turn + 1

        li.append(train_game.game_deep_copy(train_game, train_game.color))

        return li, train_game


def send_game_data_to_csv(game_list, final_game):
    winner = final_game.winner
    for idx, elem in enumerate(game_list):
        if idx % 2 == 0:
            color = 'W'
        else:
            color = 'G'
        win = color == winner
        santorini_data = SantoriniData(elem, win).data
        append_list_as_row('game_list.csv', santorini_data)
        print(idx, ':\n', elem, '\n', santorini_data)


if __name__ == '__main__':
    train_game = game.Game()
    train_game.randomize_placement('W')
    train_game.randomize_placement('G')
    train_game = train_game.game_deep_copy(train_game, 'W')
    print(train_game)
    li = []
    while not train_game.end:
        mcts_game_tree = MCTS.TreeSearch(train_game)
        mcts_game_tree.search_tree(15)
        best_node = mcts_game_tree.get_best_move()
        train_game.board = best_node.game.board
        train_game.end = best_node.game.end
        train_game.winner = best_node.game.winner

        if not train_game.end:
            train_game.turn = best_node.game.turn
        else:
            train_game.turn = best_node.game.turn + 1

        li.append(train_game.game_deep_copy(train_game, train_game.color))

    winner = train_game.winner
    for idx, elem in enumerate(li):
        if idx % 2 == 1:
            color = 'W'
        else:
            color = 'G'
        win = color == winner
        santorini_data = SantoriniData(elem, win).data
        append_list_as_row('game_list.csv', santorini_data)
        print(idx, ':\n', elem, '\n', santorini_data)
