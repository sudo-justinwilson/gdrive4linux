class Tree:
    """
    This is the base ADT for a tree.
    """
    ## start nested class =>
    class Position:
        """
        Object that abstracts the position of an single element.
        """
        def element(self):
            """
            Return the element of this position.
            This should return the custom object, which has the details of the file.
            """
            raise NotImplementedError('This is an ADT object. Concrete sub-class required!')

        def __eq__(self, other):
            """
            Return true if other Position is the same as other.
            """
            raise NotImplementedError('This is an ADT object. Concrete sub-class required!')

        def __ne__(self, other):
            """
            Return True if different from other.
            """
            return not (self == other)
    ## end nested class =>
    def root(self):
        """
        Return Position representing the tree's root (or None if empty).
        """
        raise NotImplementedError('This is an ADT object. Concrete sub-class required!')

    def parent(self, p):
        """
        Return position of p's parent (or None if p is root).
        """
        raise NotImplementedError('This is an ADT object. Concrete sub-class required!')

    def num_children
