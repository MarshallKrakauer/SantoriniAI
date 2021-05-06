"""Tree for alpha beta pruning."""
import pickle
from queue import Queue


class MiniMaxNode:
    """
    Individual node of tree used for alpha beta pruning.

    Attributes
    ----------
    game : Game
        Santorini game scored inside the node
    children : list
        list of child nodes, ie potential moves
    parent : MiniMaxNode
        parent node, ie what board looked like before this move
    score:
        How good or bad of a game it is for that player. Used for alpha-beta pruning & minimax
    """

    def __init__(self, game, children, parent=None, score=0):
        self.game = game
        self.children = children
        self.parent = parent
        self.score = score

    def __repr__(self):
        """
        Representation of node when printed.

        Returns
        -------
         str
            board with its level and score
        """
        return ('\n'
                + 'score: ' + str(self.score) + '\n'
                + str(self.game)
                )

    @staticmethod
    def create_potential_moves(node, move_color, eval_color):
        """
        Add list of possible moves to game state.
        Parameters
        ----------
        node : MiniMaxNode
            Parent node of all potential moves
        move_color : char, optional
            Player color, G or W
        eval_color:
            Color used to produce the board score
        Returns
        -------
        return_li : list
            Children of that node
        """
        return_li = []
        # Check both of the spaces occupied by the player
        for spot in [(i, j) for i in range(5) for j in range(5) if
                     node.game.board[i][j]['occupant'] == move_color]:
            i, j = spot
            # check each possible move

            for space in node.game.get_movable_spaces(game=node.game, space=(i, j)):

                new_game = node.game.game_deep_copy(node.game, move_color)
                new_game.select_worker(move_color, i, j)

                new_game.move_worker(space[0], space[1], auto=True)
                if new_game.is_winning_move():
                    return [MiniMaxNode(
                        game=new_game,
                        score=new_game.get_board_score(move_color),
                        parent=node,
                        children=None)]

                if new_game.end:
                    return_li.append(MiniMaxNode(
                        game=new_game,
                        score=new_game.get_board_score(move_color),
                        parent=node,
                        children=None))
                else:
                    # given a legal move, check for each possible build
                    for build in new_game.get_buildable_spaces(new_game, (new_game.col, new_game.row)):
                        build_game = new_game.game_deep_copy(new_game,
                                                             new_game.color)

                        build_game.build_level(build[0], build[1], auto=True)
                        if build_game.end:
                            new_score = build_game.get_board_score(eval_color)
                        else:
                            new_score = 0

                        return_li.append(MiniMaxNode(
                            game=build_game,
                            score=new_score,
                            parent=node,
                            children=[]))
        return return_li

    @staticmethod
    def alpha_beta_move_selection(root_node, depth, alpha=-10 ** 5, beta=10 ** 5, move_color='G', eval_color='G',
                                  is_max=True):
        root_game = root_node.game
        # End game, don't need to check child nodes
        if root_node.game.end:
            if eval_color != move_color:
                return 10 ** 5, None
            else:
                return -10 ** 5, None

        if depth == 0:
            return root_node.game.get_board_score(root_game.get_opponent_color(move_color)), None

        potential_nodes = root_node.create_potential_moves(node=root_node, move_color=move_color,
                                                           eval_color=eval_color)
        best_node = None  # potential_nodes[0]

        if is_max:
            current_value = -10 ** 5

            for node in potential_nodes:
                node.game.color = root_game.get_opponent_color(move_color)
                results = root_node.alpha_beta_move_selection(root_node=node, depth=depth - 1, alpha=alpha, beta=beta,
                                                              move_color=root_game.get_opponent_color(move_color),
                                                              eval_color=eval_color,
                                                              is_max=not is_max)

                if current_value < results[0]:
                    current_value = results[0]
                    alpha = max(alpha, current_value)
                    best_node = node

                if beta <= alpha:
                    break

            if best_node is None:
                return current_value, None

        else:
            current_value = 10 ** 5
            for node in potential_nodes:
                node.game.color = root_game.get_opponent_color(move_color)
                results = root_node.alpha_beta_move_selection(root_node=node, depth=depth - 1, alpha=alpha, beta=beta,
                                                              move_color=root_game.get_opponent_color(move_color),
                                                              eval_color=eval_color,
                                                              is_max=not is_max)

                if current_value > results[0]:
                    current_value = results[0]
                    beta = min(beta, current_value)
                    best_node = node

                if beta <= alpha:
                    break

            if best_node is None:
                return current_value, None

        return current_value, best_node

    @staticmethod
    def is_terminal(node):
        """
        Find if node has children.

        Parameters
        ----------
        node : MiniMaxNode
            Node to check for children
        Returns
        -------
        bool
            True if node is leaf node (ie no children)
        """
        return len(node.children) == 0

    @staticmethod
    def print_depth_first(root):
        """
        Print value of nodes in depth first order.

        Parameters
        ----------
        root : MiniMaxNode
            root node of tree to search
        Returns
        -------
        None.
        """
        print(root.score)
        for tree in root.children:
            tree.print_depth_first(tree)


def store_breadth_first(root, print_nodes=False):
    """
    Print values breadth first (level by level).

    Parameters
    ----------
    root : MiniMaxNode
        root node of tree to search
    print_nodes: bool
        if true, prints boards while storing pkl file
    Returns
    -------
    q : Queue
        Nodes values in breadth first order
    """
    q = Queue(maxsize=1000000)
    li = [root]
    q.put(root)
    while not q.empty():
        curr_node = q.get()
        for node in curr_node.children:
            if print_nodes:
                print(node)
            li.append(node)
            q.put(node)

    with open('alpha_queue.pkl', 'wb') as f:
        pickle.dump(li, f)
    return q
