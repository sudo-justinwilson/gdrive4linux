class Tree:
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

    def __init__(self, root):
        """
        Initialize an empty tree structure.
        """
        self.root = self.Node(self.File(*args))
        self.root.children = dict()
        #self.size = 1

    def add_child_node(self, element, parent=self.root):
        """
        Add a child node to the parent.
        'element' must be of the type self.File.
        """
        if not isinstance(element, (self.File)):
            raise TypeError('The first arg (element) must be of the type self.File')
        parent.children[element.file_id] = element

    def nodes(self, parent=self.root):
        """
        Return the children's elements.
        """
        for child in parent.children:
            yield parent[child]

    def elements(self, parent):
        for node in parent.nodes:
            yield node.element

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
