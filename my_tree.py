from my_tree_ADT import Tree_ADT

class my_tree(Tree_ADT):
    """ 
   This is my implementation of a general tree structure to store metadata about the google drive files.
    """ 
    class Node:
        """
        A simple data structure that will act as nodes in the tree.
        """
        __slots__ = 'parent', 'children', 'element'

        def __init__(self, parent, element):
            """
            Initialize a simple Node instance
            """
            self.parent = parent
            self.element = element
            self.children = None

    ##  End nested Node class       ##
    ##  Begin nested file class     ##
    class File:
        """
        This is a data structure where I can store the metadata of a file.
        """
        __slots__ == 'file_id', 'title', 'mime_type', 'md5', 'parent' 
        def __init__(self, file_id, title, mime_type, parent, md5 = None):
            """
            Initialize a File object with provided metadata.
            """
            self.file_id = file_id
            self.title = title
            self.mime_type = mime_type
            self.parent = parent
            self.md5 = md5

    ##  End nested file class       ##
    ##  S
    ##  End nested classes           ##
    def __init__(self, root):
        """
        Initialize an empty tree.
        """
        self.root = self.Node(None, element)
        self.size = 1
        self.root.children = dict()

    def _make_path_from_string(self, PATH):
        """
        Return the node of the path = PATH.
        PATH should be a string. IE: "$DRIVE_ROOT_DIR/Books/Calibre/mybook.pdf".
        The path should be relative from the GDRIVE_ROOT_DIR.
        Returns a tuple with (Node(parent), str(file_title)).
        """
        l = PATH.split('/')
        current_parent = l.pop(0)
        while len(l) > 1:
            current_parent = current_parent.children[l.pop(0)]
        file_title = current_parent[-1]
        return (current_parent, file_title)

    def add_child_node(self, n, parent):
        """
        Add node 'n' as a child to parent.
        """
        parent.children[file_id] = self.Node(parent, element)





###     THIS IS THE OLD CODE BELOW:
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
