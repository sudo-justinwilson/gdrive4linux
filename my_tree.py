from trethsee_ADT import Tree

class my_tree(Tree):r
    """ 
   This is my implementation of a general tree structure to store metadata about the google drive files.
    """ 
    def root(self):
        """
        Return the position of the root of the tree, or None if is empty.
        """
        
    def is_root(self,p):
        """
        Return True if p is root.
        """
        if p.parent is None:
            return True
        else:
            return False

    def parent(self, p):
        """
        Return the position of the parent of position "p", or None if p is the root.
        """

    def num_children(self, p):
        """
        Return the number of children of position p.
        """
        if p.MIME == 'directory':
            return p.num_children
        else:
            print('This item has no children.')

    def children(self, p):
        """
        Generate an iteration of children of position p.
        """
        generator = { child for child in children }

    def is_leaf(p):
        """
        Return True if p is leaf.
        """
        if self.num_children(p) > 0:
            return False
        else:
            return True

    def len(self, T):
        """
        Return the number of positions (and hence elements) that are contained in tree T.
        """
        if isinstance(T, (type(self))):
            return T.length
        else:
            raise Exception

    def is_empty(self):
        """
        Return True if tree T does not contain any positions.
        """
        if self.len() > 0:
            return False
        else:
            return True

    def positions(self):
        """
        Generate an iteration of all positions of tree T.
        """


    def iter(self, T):
        """
        Generate an iteration of all elements stored within tree T.
        """
