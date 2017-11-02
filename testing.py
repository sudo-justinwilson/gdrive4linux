"""
This module contains functions for debugging.
"""
def debug(flag, *text):
    """
    If flag is set to True: print text.
    """
    if flag:
        print(''.join(text))

if __name__ == '__main__':
    verbose = False
    debug(verbose, 'the id of the file is %s' % 'justin')
