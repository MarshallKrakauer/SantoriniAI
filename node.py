"""Tree for alpha beta pruning."""
from queue import Queue

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

    def __init__(self, value=None, children=None, state=None, level=0):
        self._value = value
        self._children = children
        self._state = state
        self._level = level

    def __repr__(self):
        """
        Representation of node when printed.

        Returns
        -------
         str
            board with its level and score
        """
        return ('\nscore: ' + str(self._state.evaluate_board()) + '\n'
                + 'level ' + str(self._level) + '\n'
                + str(self._state)
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

        best_state = None
        for elem in self.children:
            value = self.min_value(elem, best_val, beta)
            # time.sleep(1)
            # print(dt.datetime.now())
            # print(self)
            if value > best_val:
                best_val = value
                best_state = elem.state

        return best_state

    @property
    def children(self):
        """Return children of Node."""
        return self._children

    @property
    def value(self):
        """Return value (score) of Node's game."""
        return self._value

    @property
    def state(self):
        """Return the Game class."""
        return self._state

    @property
    def level(self):
        """Return the level (ie layer parent nodes)."""
        return self._level

    @children.setter
    def children(self, children):
        """Return node's children in the tree."""
        self._children = children

    @state.setter
    def state(self, state):
        """Set Node's Game to another Game."""
        self._state = state

    @value.setter
    def value(self, value):
        """Set score of Game's board."""

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


def print_breadth_first(root, level=0):
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
    q = Queue(maxsize=100)
    q.put(root)
    while not q.empty():
        curr_node = q.get()
        print(curr_node.value, curr_node.level)
        for idx, n in enumerate(curr_node.children):
            if idx == 0:
                level += 1
            q.put(n)
    return q
