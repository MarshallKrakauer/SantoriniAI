"""Gather data from a Santorini Game. Will be used to make predictive model"""

import game
import pandas as pd
from time import time
from math import sqrt

SPACE_LIST = [(i, j) for i in range(5) for j in range(5)]


class SantoriniData:

    def __init__(self, santorini_game):
        self.data = self.get_board_data(santorini_game)

    def get_board_data(self, santorini_game):
        santorini_game_data = []
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

        turn = santorini_game.turn

        our_color_levels = self.worker_level_sort(our_color_levels)
        other_color_levels = self.worker_level_sort(other_color_levels)
        our_color_levels.extend(other_color_levels)

        for x in our_color_levels:
            santorini_game_data.extend(self.make_list(x))

        santorini_game_data.append(turn)
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

        for elem in self_cols:
            for num in [0, 1, 2, 3, 4]:
                col_list.append(elem + '_' + str(num))

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
test_game = game.Game()
test_game.color = 'W'
test_game.board[2][0]['occupant'] = 'G'
test_game.board[2][2]['level'] = 2
test_game.board[2][1]['level'] = 3
test_game.board[0][3]['occupant'] = 'G'
test_game.board[1][3]['level'] = 2

test_game.board[2][2]['occupant'] = 'W'
test_game.board[2][2]['level'] = 2
test_game.board[3][3]['level'] = 3
test_game.board[4][4]['occupant'] = 'W'
test_game.board[4][4]['level'] = 1

# </editor-fold>


if __name__=='__main__':
    t0 = time()
    for i in range(10 ** 5):  # 100k runs
        test_li = SantoriniData(test_game).data
    t1 = time()
    print(t1 - t0)




