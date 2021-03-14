from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

from game import Game, SPACE_LIST

EMPTY_MATRIX = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]


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


def find_path(path_matrix,start_coordinates, end_coordinates, print_path=False):
    grid = Grid(matrix=path_matrix)
    start = grid.node(start_coordinates[0], start_coordinates[1])
    end = grid.node(end_coordinates[0], end_coordinates[1])

    finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
    path, runs = finder.find_path(start, end, grid)

    if print_path:
        print('operations:', runs, 'path length:', len(path))
        print(grid.grid_str(path=path, start=start, end=end))

    return len(path)


def main():
    test_game = Game()
    test_game.board[2][0]['level'] = 4
    test_game.board[2][1]['level'] = 4
    test_game.board[2][2]['level'] = 4
    test_game.board[2][3]['level'] = 4

    test_game.board[0][0]['occupant'] = 'W'
    test_game.board[4][4]['occupant'] = 'W'

    li = get_colors(test_game, 'W')

    test_matrix = create_matrix(test_game, li[0], 'W')
    find_path(test_matrix, li[0], li[1])


if __name__ == '__main__':
    main()
