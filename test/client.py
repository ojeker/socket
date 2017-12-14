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

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

        self._initial_action()

    def onMessage(self, payload, isBinary):
        if isBinary:
            raise Exception('Binary message received')

        text = payload.decode('utf8')
        ltext = text.lower()
        if ltext.startswith('ready'):
            self._ready_received(text)
        elif ltext.startswith('error'):
            self._error_received(text)
        else:
            self._message_received(text)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
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

    def _ready_received(self, message):
        """Hook to react to finished handshake"""
        pass

    def _stop_client(self):
        loop = asyncio.get_event_loop()
        loop.stop()


class TestClient(WebSocketClientProtocol):

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

        text = 'bcd7e841-86bc-4225-9502-01637fd1f1aa' + ':' + self.connect_type()
        self.send_text(text)

    def connect_type(self):
        raise NotImplementedError()
        return 'VOID'

    def send_text(self, text):
        encoded = text.encode('utf8')
        self.sendMessage(encoded)

    def onMessage(self, payload, isBinary):
        if isBinary:
            raise Exception('Binary message received')

        text = payload.decode('utf8')
        if text.startswith('ready'):
            self.send_text('hello world')


        # elif text.startswith('hello'):
        #     self.sendClose()
        # else:
        #     raise Exception('Unexpected message received')

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self._stop_client()

    def _stop_client(self):
        loop = asyncio.get_event_loop()
        loop.stop()

class GisClient(TestClient):
    def connect_type(self):
        return 'gisConnect'

class AppClient(TestClient):
    def connect_type(self):
        return 'appConnect'


class Hijacker(WebSocketClientProtocol):
    """
    Client trying to connect to session that already accepted
    a connection.
    """

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

        text = 'bcd7e841-86bc-4225-9502-01637fd1f1aa' + ':' + self.connect_type()
        self.send_text(text)

    def connect_type(self):
        raise NotImplementedError()
        return 'VOID'

    def send_text(self, text):
        encoded = text.encode('utf8')
        self.sendMessage(encoded)

    def onMessage(self, payload, isBinary):
        if isBinary:
            raise Exception('Binary message received')

        text = payload.decode('utf8')
        if text.startswith('Error 504'):
            self.sendClose()
        else:
            raise Exception('Unexpected message received')

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self._stop_client()

    def _stop_client(self):
        loop = asyncio.get_event_loop()
        loop.stop()


class GisHijacker(Hijacker):
    """Hijacker connecting as gis client"""

    def connect_type(self):
        return 'gisConnect'