from my_tree_ADT import Tree_ADT

class Tree(Tree_ADT):
    """
    Tree to store google drive file metadata.
    """
    class Node:
        """
        A simple data structure that will act as nodes in the tree.
        """
        __slots__ = 'parent', 'children', 'element'
    
        def __init__(self, element, parent=None):
            """
            Initialize a simple Node instance
            """
            self.parent = parent
            self.element = element
            self.children = None
    ##  End nested Node class       ##

    def __init__(self, element):
        """
        Initialize an empty tree structure.

        Args:
            element:    This is the element that the root node will point to.
        """
        #self.root = self.Node(self.File(*args))
        self.root = self.Node(element, None)
        self.root.children = dict()
        self.size = 1

    def add_node(self, element, parent):
        """
        Add a child node to the parent.
        'element' and 'parent' must be of the type self.File.
        """
        if not isinstance(parent, (self.Node)):
            raise TypeError('The second arg (parent) must be of the type self.Node')
        # Set parent.children to an empty dict:
        parent.children = {}
        # Add a member to parent.children:
        parent.children[element.file_id] = element

    def delete_node(self, child, parent):
        """
        Delete child node from parent, and return deleted node.
        """
        if not isinstance(parent, (self.Node)):
            raise TypeError('The second arg (parent) must be of the type self.Node')
        if node not in parent.children.keys():
            raise NameError(node + ' is not a child of of the parent')
        return parent.children.pop(child)

    def nodes(self, parent):
        """
        Iterate through the children nodes of a parent.
        """
        for child in parent.children:
            yield parent
        
        for node in parent.nodes:
            yield node.element

    def __iter__(self, parent):
        """
        Iterate through the elements of a parent.
        """
        for child in parent.children:
            yield parent.children[child].element

    def add_node_from_path(self, path):
        """
        Add node from path.
        'path' must be a string and the path must be relative from the google drive root directory
        """
        PATH = path.split('/')
        current_parent_node = PATH.pop(0)
        length = len(PATH)
        if not current_parent_node == self.root:
            raise Exception('The path is not relative from google drive root directory.')
        ##
        while length(PATH) > 1:
            if PATH[0] not in { v.element.title for v in current_parent_node.children.values() }:
                raise Exception('Could not find ' + PATH[0] + ' in ' + current_parent_node.element.path)
            current_parent_node = current_parent_node.children[PATH.pop(0)]
            if not isinstance(current_parent_node, (self.Node)):
                raise TypeError('The add_node_from_path() method did not return a Node instance.')
