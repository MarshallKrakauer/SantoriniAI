"""Tree for alpha beta pruning."""
from queue import Queue
import pickle


class Node:
    """
    Individual node of tree used for alpha beta pruning.

    Attributes
    ----------
    value : int
        Score of the Santorini game. Used for alpha-beta pruning
    children : list
        list of child nodes
    state : Game
        Santorini game to produce store of
    end : level
        Number of parent nodes. Root node has level 0
    """

    def __init__(self, game, children=[], level=0, max_level=2, parent = None):
        self.game = game
        self.value = self.game.evaluate_board()
        self.children = children
        self.level = level
        self.max_level = max_level
        self.parent = parent

    def __repr__(self):
        """
        Representation of node when printed.

        Returns
        -------
         str
            board with its level and score
        """
        return ('\n'
                + 'level ' + str(self.level) + '\n'
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
            return node.value
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
            return node.value
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
    Node : Node
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
    print(root.value)
    for tree in root.children:
        print_depth_first(tree)


def print_breadth_first(root, create_pickle = True):
    """
    Print values breadth first (level by level).

    Parameters
    ----------
    root : Node
        root node of tree to search
    level : int
        Level of tree, parent being 0 by default
    Returns
    -------
    q : Queue
        Nodes values in breadth first order
    """
    q = Queue(maxsize=100000)
    li = []
    li.append(root)
    q.put(root)
    while not q.empty():
        curr_node = q.get()
        for node in curr_node.children:
            print(node)
            li.append(node)
            q.put(node)
            
    if create_pickle:
        with open('alpha_queue.pkl', 'wb') as f:
            pickle.dump(li, f)
    return q
