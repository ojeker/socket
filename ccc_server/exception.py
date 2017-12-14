"""Contains all exception classes used in the CCC server"""

class CCCException(Exception):
    """Base class for all Exceptions raised in the CCC Server application"""
    def __init__(self, msg):
        super().__init__(msg)

class ProtocollError(CCCException):
    """Base class for all error's throws if a ccc protocoll related error occured"""

    def __init__(self, num, msg):
        """Creates a new object with the given error num and error msg"""
        super().__init__(msg)
        self.num = num

class Error504(ProtocollError):
    """Error thrown on the server when another client tries to connect to the same session"""

    def __init__(self, session_id, client_type):
        num = 504
        msg = 'Error {} - can not join session. A [{}] client is already connected to session [{}]'.format(
            num, client_type, session_id)
        super().__init__(num, msg)


class Error503(ProtocollError):
    """
    Error thrown on the server when messages to the receiving client are sent before the client - client
    handshake ist finished.
    """

    def __init__(self):
        num = 503
        super().__init__(
            num,
            'Error {} - can not forward message as the client - client handshake ist not finished'.format(num)
        )
