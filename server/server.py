from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory


class CCCServer():
    """Singleton instance of the CCCServer running and accepting new WebSocket connections"""
    __instance = None

    @staticmethod
    def instance():
        if CCCServer.__instance is None:
            CCCServer.__instance = CCCServer()

    def __init__(self):
        import asyncio

        self.sessionDict = dict

        factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
        factory.protocol = SocketServerConnection

        loop = asyncio.get_event_loop()
        coro = loop.create_server(factory, '0.0.0.0', 9000)
        server = loop.run_until_complete(coro)

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.close()
            loop.close()

    def addClientConnection(self, clientConn):
        """Adds a session in state [leaf_connected] to the session dictionary."""
        self.sessionDict[session.uid] = session


class SocketServerConnectionWrapper():
    """
    WebSocket Connection between a Client and the CCC-Server
    for sending and receiving text.
    Handels the connection (opening, closing) and allows to force
    close the Connection from the outside.
    """

    def close(self):
        """Forces the connection to the corresponding client to be closed"""
        pass

    def setCloseListener(self, closeListenerFunc):
        """Set's the function that will be called when this Connection ist closed"""
        pass

    def setTextReceivedListener(self, textRecievedFunc):
        """Set's the function that will be called when this Connection recieves a text message from the client"""
        pass

    def sendText(self, textMessage):
        """Send's the given text message to the client"""
        pass


class SocketServerConnection(WebSocketServerProtocol):
    """Connection between the server and one chat client"""

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            raise CCCException("Received binary data - should only be text")

        #todo gogon message = decode utf 8 ...

        # echo back message verbatim
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':
    CCCServer.instance()
