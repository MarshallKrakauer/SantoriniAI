"""
Pseudo-pathfinder that will find how far apart a player's two pieces are.

This will be used as part of the scoring function. I call it a pseudo-pathfinder because it doesn't account
for the changes in height as player moves across the board. I'm simplifying to save both production time
and run time. The current file tests the pathfinder.
"""

import numpy as np
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

EMPTY_MATRIX = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
SPACE_LIST = [(i, j) for i in range(5) for j in range(5)]


def get_colors(game, color):
    space_li = []
    for col, row in SPACE_LIST:
        if game.board[col][row]['occupant'] == color:
            space_li.append((col, row))

    return space_li


def create_matrix(game, space, color):
    column, row = space
    path_matrix = EMPTY_MATRIX
    movable_level = game.board[column][row]['level'] + 1
    for column, row in SPACE_LIST:
        if game.board[column][row]['occupant'] == color:
            path_matrix[row][column] = 1
        elif game.board[column][row]['level'] > movable_level:
            path_matrix[row][column] = 0
        elif game.board[column][row]['occupant'] != 'O':
            path_matrix[row][column] = 0
        else:
            path_matrix[row][column] = 1
    return path_matrix


def find_path(path_matrix, start_coordinates, end_coordinates, print_path=False):
    grid = Grid(matrix=path_matrix)
    start = grid.node(start_coordinates[0], start_coordinates[1])
    end = grid.node(end_coordinates[0], end_coordinates[1])

    finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
    path, runs = finder.find_path(start, end, grid)

    if print_path:
        print('operations:', runs, 'path length:', len(path))
        print(grid.grid_str(path=path, start=start, end=end))

    return len(path)


def get_path_score(game, color):
    space_list = get_colors(game, color)

    matrix_0 = create_matrix(game, space_list[0], color)
    matrix_1 = create_matrix(game, space_list[1], color)
    num_0 = find_path(matrix_0, space_list[0], space_list[1])
    num_1 = find_path(matrix_1, space_list[1], space_list[0])

    if num_0 == 0:
        num_0 = 15
    else:
        num_0 = np.min([num_0, 15])

    if num_1 == 0:
        num_1 = 15
    else:
        num_1 = np.min([num_1, 15])

    return num_0 + num_1
