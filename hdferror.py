#hdfErrors

class Error(Exception):
    """Base class for exceptions in this module."""
    def __init__(self):
        pass

class WrongFile(Error):
    """docstring for WrongFile"""
    def __init__(self, arg):
        self.arg = arg
