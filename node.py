"""Tree for alpha beta pruning."""
from queue import Queue
#from game import Game, create_potential_moves, game_deep_copy
import pickle


# noinspection PyDefaultArgument
class Node:
    """
    Individual node of tree used for alpha beta pruning.

    Attributes
    ----------
    game : Game
        Santorini game scored inside the node
    children : list
        list of child nodes, ie potential moves
    level : level
        Number of parent nodes. Root node has level 0
    max_level : int
        Level at bottom of the tree, ie how many moves ahead to look
    parent : Node
        parent node, ie what board looked like before this move
    score:
        How good or bad of a game it is for that player. Used for alpha-beta pruning & minimax
    """

    def __init__(self, game, children=[], level=0, max_level=2, parent=None,
                 score=0):
        self.game = game
        self.children = children
        self.level = level
        self.max_level = max_level
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
                + 'level: ' + str(self.level) + '\n'
                + 'score: ' + str(self.score) + '\n'
                + str(self.game)
                )

    def min_value(self, node, alpha, beta):
        """
        Min portion of alpha-beta pruning.

        Parameters
        ----------
        node : Node
            node with board, state, and children
        alpha : int
            alpha value for alpha-beta pruning algorithm
        beta : TYPE
            beta value for alpha-beta pruning algorithm
        Returns
        -------
        int
            smallest value found among tree's children
        """

        if is_terminal(node):
            return node.score

        value = float('inf')

        for elem in node.children:
            value = min(value, self.max_value(elem, alpha, beta))
            if value <= alpha:
                return value
            beta = min(beta, value)

        return value

    def max_value(self, node, alpha, beta):
        """
        Max portion of alpha-beta pruning.

        Parameters
        ----------
        node : Node
            node with board, state, and children
        alpha : int
            alpha value for alpha-beta pruning algorithm
        beta : TYPE
            beta value for alpha-beta pruning algorithm
        Returns
        -------
        int
            greatest value found among tree's children
        """
        if is_terminal(node):
            return node.score
        value = -float('inf')

        for elem in node.children:
            value = max(value, self.min_value(elem, alpha, beta))
            if value >= beta:
                return value
            alpha = max(alpha, value)

        return value

    def alpha_beta_search(self):
        """
        Conducts alpha-beta search on the root node for best move.

        Returns
        -------
        best_state : Game
            game with the highest scores
        """
        best_val = -float('inf')
        beta = float('inf')

        best_move = None
        for elem in self.children:
            value = self.min_value(elem, best_val, beta)
            if value > best_val:
                best_val = value
                best_move = elem.game

        return best_move




def is_terminal(node):
    """
    Find if node has children.

    Parameters
    ----------
    node : Node
        Node to check for children
    Returns
    -------
    bool
        True if node is leaf node (ie no children)
    """
    return len(node.children) == 0


def print_depth_first(root):
    """
    Print value of nodes in depth first order.

    Parameters
    ----------
    root : Node
        root node of tree to search
    Returns
    -------
    None.
    """
    print(root.score)
    for tree in root.children:
        print_depth_first(tree)


def store_breadth_first(root, print_nodes=False):
    """
    Print values breadth first (level by level).

    Parameters
    ----------
    root : Node
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
