class Tree_ADT:
    """
    Simple tree structure to be used as the base tree ADT.
    """
    #class Node:
    #    """
    #    A simple data structure that will act as nodes in the tree.
    #    """
    #    __slots__ = 'parent', 'children', 'element'
    #    def __init__(self, parent, element):
    #        """
    #        Initialize a simple Node instance
    #        """
    #        self.parent = parent
    #        self.element = element

    ##  End nested Node class       ##
    #def __init__(self, root):
    #    """
    #    Initialize an empty tree_ADT.
    #    """
    #    self.root = self.Node(None, element)
    #    self.size = 1
    #    self.root.children = dict()

    def add_node(self):
        """
        Add a child node to parent.
        """
        raise NotImplementedError('Needs to be implemented by subclass')

    def delete_node(self):
        """
        Add a child node to parent.
        """
        raise NotImplementedError('Needs to be implemented by subclass')

    def parent(self, node):
        """
        Return parent of node.
        """
        raise NotImplementedError('Needs to be implemented by subclass')

    def is_root(self, n):
        """
        Return True if n is root node.
        """
        return self.root() == n

    def is_leaf(self, n):
        """
        Return True if n is leaf node.
        """
        return n.children is None

    def nodes(self, parent=root):
        """
        Iterate through the children nodes.
        """
        raise NotImplementedError('Needs to be implemented by subclass')

    def __len__(self, node=self.root):
        raise NotImplementedError('Needs to be implemented by subclass')

    def __iter__(self):
        """
        Iterate through the tree's elements.
        """
        raise NotImplementedError('Needs to be implemented by subclass')
