"""Contains all exception classes used in the CCC server"""

class CCCException(Exception):
    """Base class for all Exceptions raised in the CCC Server application"""

    def __init__(self, message):
        self.message = message