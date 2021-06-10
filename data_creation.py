"""Gather data from a Santorini Game. Will be used to make predictive model"""

import game
import pandas as pd
from math import sqrt

SPACE_LIST = iter([(i, j) for i in range(5) for j in range(5)])


def worker_level_sort(worker_list):
    if worker_list[0] > worker_list[9]:
        temp = worker_list[0:9]
        worker_list[0:9] = worker_list[9:18]
        worker_list[9:18] = temp

    return worker_list


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


def distance_between(col_0, row_0, col_1, row_1):
    """Geometrics distance between two points"""
    return sqrt((col_0 - col_1) ** 2 + (row_0 - row_1) ** 2)


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


def make_list(worker_level):
    return_list = [0, 0, 0, 0, 0]
    return_list[worker_level] = 1
    return return_list


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

our_color = []
other_color = []

player_space = []
player_space_adj = []
other_space = []
other_space_adj = []

for i, j in SPACE_LIST:
    if test_game.board[i][j]['occupant'] == test_game.color:
        our_color.append(test_game.board[i][j]['level'])
        player_space.append((i, j))
        adj = get_adjacent(i, j, test_game)
        adj.sort()
        our_color.extend(adj)
    elif test_game.board[i][j]['occupant'] == test_game.opponent_color:
        other_color.append(test_game.board[i][j]['level'])
        other_space.append((i, j))
        adj = get_adjacent(i, j, test_game)
        adj.sort()
        other_color.extend(adj)



player_col_0, player_row_0 = player_space[0]
player_col_1, player_row_1 = player_space[1]

opponent_col_0, opponent_row_0 = other_space[0]
opponent_col_1, opponent_row_1 = other_space[1]

opponent_distance = [distance_between(player_col_0, player_row_0, opponent_col_0, opponent_row_0),
                     distance_between(player_col_0, player_row_0, opponent_col_1, opponent_row_1),
                     distance_between(player_col_1, player_row_1, opponent_col_1, opponent_row_1),
                     distance_between(player_col_1, player_row_1, opponent_col_0, opponent_row_0)]

self_distance = distance_between(player_col_0, player_row_0, player_col_1, player_row_0)

our_color = worker_level_sort(our_color)
other_color = worker_level_sort(other_color)
our_color.extend(other_color)
# </editor-fold>

new_li = []
for x in our_color:
    new_li.extend(make_list(x))

print(len(make_columns()), len(new_li))
