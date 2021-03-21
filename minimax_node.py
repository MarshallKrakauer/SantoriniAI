"""Tree for alpha beta pruning."""
from queue import Queue
import pickle


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

    def __init__(self, game, children, parent=None,
                 score=0):
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
        print_depth_first(tree)


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
