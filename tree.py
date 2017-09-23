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
    
        def __init__(self, element, parent):
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
        self.root = self.Node(element, None)
        self.size = 1

    def add_node(self, element, parent):
        """
        Add a child node to the parent.
        'element' and 'parent' must be of the type self.File.
        """
        if not isinstance(parent, (self.Node)):
            raise TypeError('The second arg (parent) must be of the type self.Node')
        # Set parent.children to an empty dict:
        if parent.children is None:
            parent.children = {}
        # Add a member to parent.children:
        #parent.children[element.file_id] = element
        parent.children[element.file_id] = self.Node(element, parent)
        self.size += 1

    def delete_node(self, child, parent):
        """
        Delete child node from parent, and return deleted node.
        """
        if not isinstance(parent, (self.Node)):
            raise TypeError('The second arg (parent) must be of the type self.Node')
        #if child not in parent.children.keys():
        #    raise NameError(child, ' is not a child of of the parent')
        if child not in parent.children:
            raise NameError(child, ' is not a child of of the parent')
        self.size -= 1
        return parent.children.pop(child)

    def __len__(self):
        """
        Return the number of nodes in the tree.
        """
        return self.size

    def nodes(self, parent):
        """
        Iterate through the children nodes of a parent.
        """
        for child in parent.children:
            yield parent.children[child]

    #def add_node_from_path(self, path):
    #    """
    #    Add node from path.
    #    'path' must be a string and the path must be relative from the google drive root directory
    #    """
    #    PATH = path.split('/')
    #    current_parent_node = PATH.pop(0)
    #    length = len(PATH)
    #    if not current_parent_node == self.root:
    #        raise Exception('The path is not relative from google drive root directory.')
    #    ##
    #    while length(PATH) > 1:
    #        if PATH[0] not in { v.element.title for v in current_parent_node.children.values() }:
    #            raise Exception('Could not find ' + PATH[0] + ' in ' + current_parent_node.element.path)
    #        current_parent_node = current_parent_node.children[PATH.pop(0)]
    #        if not isinstance(current_parent_node, (self.Node)):
    #            raise TypeError('The add_node_from_path() method did not return a Node instance.')

if __name__ == '__main__':
    class File:
        __slots__ = 'name', 'file_id', 'type'
        def __init__(self, name, file_id, type):
            self.name = name
            self.file_id = file_id
            self.type = type
    tree = Tree(File('j.w.winship@gmail.com', '454f34t4', 'directory'))
    print('tree introspection: ', dir(tree))
    print('the size of the tree is: ', tree.size)
    tree.add_node(File('file1', '3rfd234r', 'directory'), tree.root)
    tree.add_node(File('file2', 'g43t4rf', 'pdf'), tree.root)
    tree.add_node(File('file3', 'g4t43trfg4', 'docs'), tree.root)
    tree.add_node(File('file4', '4er9ij4kr', 'sheet'), tree.root)
    print('the size of the tree is: ', tree.size)
    print('this is the root nodes element name attr: ', tree.root.element.name)
    print('deleting tree.root.children[' + '4er9ij4kr' + ']')
    print(tree.delete_node('4er9ij4kr', tree.root).element.name)
    print(tree.delete_node('3rfd234r', tree.root).element.name)
    print(tree.delete_node('g43t4rf', tree.root).element.name)
    print(tree.delete_node('g4t43trfg4', tree.root).element.name)
    print('testing to see what happens when we delete a non-existent node:')
    try:
        print(tree.delete_node('4er9ij4kr', tree.root).element.name)
    except NameError as e:
        print("You tried to delete a non-existent node!", e)
    print("the size of the tree is: ", tree.size)
    tree.add_node(File("file1", "3rfd234r", "directory"), tree.root)
    tree.add_node(File("file2", "g43t4rf", "pdf"), tree.root)
    tree.add_node(File("file3", "g4t43trfg4", "docs"), tree.root)
    tree.add_node(File("file4", "4er9ij4kr", "sheet"), tree.root)
    print("the size of the tree is: ", tree.size)
    print()
    print("Testing the tree.nodes() method:")
    for node in tree.nodes(tree.root):
        print("The type of this element is:\t", type(node))
        print("Here are the members of this node:\t", dir(node))
        print("Here is the element of the current node:\t", node.element.name)
