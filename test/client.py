import asyncio
from autobahn.asyncio.websocket import WebSocketClientProtocol

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
        elif text.startswith('hello'):
            self.sendClose()
        else:
            raise Exception('Unexpected message received')

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