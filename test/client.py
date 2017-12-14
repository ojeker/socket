import asyncio
import logging
import uuid

from autobahn.asyncio.websocket import WebSocketClientProtocol

class BaseClient(WebSocketClientProtocol):
    """Base class providing the extension points for concrete test clients to work with"""

    APPLICATION = 'appConnect'
    GIS = 'gisConnect'

    def __init__(self, session_id, client_type):
        self.session_id = session_id
        self.client_type = client_type

    def __repr__(self):
        return '{} on session {}'.format(type(self), self.session_id)

    def onConnect(self, response):
        print('Server connected: {0}'.format(response.peer))

    def onOpen(self):
        print('WebSocket connection open. [{}]'.format(repr(self)))

        self._initial_action()

    def onMessage(self, payload, isBinary):
        if isBinary:
            raise Exception('Binary message received [{}]'.format(repr(self)))

        text = payload.decode('utf8')
        print('Message received. First 80 chars: {} ... [{}]'.format(text[:80], repr(self)))

        ltext = text.lower()
        if ltext.startswith('ready'):
            self._ready_received()
        elif ltext.startswith('error'):
            self._error_received(text)
        else:
            self._message_received(text)

    def onClose(self, wasClean, code, reason):
        print('WebSocket connection closed. Reason: {} [{}]'.format(reason, repr(self)))
        self._stop_client()

    def _send_text(self, text):
        """Convenience method for subclasses to send text"""
        encoded = text.encode('utf8')
        self.sendMessage(encoded)

    def _initial_action(self):
        """Hook to start an initial action for a client"""
        pass

    def _message_received(self, message):
        """Hook to react to payload messages"""
        pass

    def _error_received(self, message):
        """Hook to react to received error messages"""
        pass

    def _ready_received(self):
        """Hook to react to finished handshake"""
        pass

    def _stop_client(self):
        loop = asyncio.get_event_loop()
        loop.stop()

class Hijacker(BaseClient):
    """
    Client trying to connect to session that already accepted
    a connection.
    """
    def __init__(self, session_id, client_type):
        super().__init__(session_id, client_type)

    def _initial_action(self):
        text = self.session_id + ':' + self.client_type
        self._send_text(text)

    def _error_received(self, message):
        try:
            if message.lower().startswith('error 504'):
                self.sendClose()
            else:
                raise Exception('Unexpected message received')
        finally:
            self._stop_client()

class GisHijacker(Hijacker):
    def __init__(self):
        super().__init__(
            'bcd7e841-86bc-4225-9502-01637fd1f1aa',
            BaseClient.GIS)

class AppHijacker(Hijacker):
    def __init__(self):
        super().__init__(
            'bcd7e841-86bc-4225-9502-01637fd1f1aa',
            BaseClient.APPLICATION)

class Greeter(BaseClient):
    """'Sun path client' doing the handshake and sending a hello world to the other client"""
    def __init__(self, session_id, client_type):
        super().__init__(session_id, client_type)

    def _initial_action(self):
        text = self.session_id + ':' + self.client_type
        self._send_text(text)

    def _ready_received(self):
        self._send_text('hello world')

    def _message_received(self, message):
        try:
            if message.lower().startswith('hello world'):
                self.sendClose()
            else:
                raise Exception('Unexpected message received')
        finally:
            self._stop_client()

class AppClient(Greeter):
    def __init__(self):
        super().__init__(
            'bcd7e841-86bc-4225-9502-01637fd1f1aa',
            BaseClient.APPLICATION
        )

class GisClient(Greeter):
    def __init__(self):
        super().__init__(
            'bcd7e841-86bc-4225-9502-01637fd1f1aa',
            BaseClient.GIS
        )
