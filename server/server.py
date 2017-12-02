from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory
from datetime import datetime
from uuid import UUID
from logging import Logger


class SessionStore:
    """Singleton instance containing all sessions of the corresponding CCCServer"""
    __instance = None

    @staticmethod
    def instance():
        if SessionStore.__instance is None:
            SessionStore.__instance = SessionStore()

        return SessionStore.__instance

    def __init__(self):
        self.sessionDict = dict()

    def addClientConnection(self, clientConn, message):
        """
        If no session for the given session id exits: Creates a new session and adds it to the dict.
        Calls the sessions addClientConnection() method to ask the session to add the connection
        """
        parts = message.split(':')
        print(parts)
        session_id = UUID(parts[0])

        session = self.sessionDict.get(session_id)
        if session is None:
            session = CCCSession(session_id)
            session.addClientConnection(clientConn, parts[1])
            self.sessionDict[session_id] = session
        else:
            session.addClientConnection(clientConn, parts[1])

        return session

class SocketServerConnection(WebSocketServerProtocol):
    """Connection between the server and one chat client"""

    def __init__(self):
        super().__init__()
        self.enclosing_session = None

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        try:
            if isBinary:
                raise CCCException("Received binary data - should only be text")

            message = payload.decode('utf8')
            message = message.strip()
            print('message received: ' + message)

            if self.enclosing_session is None or not self.enclosing_session.client_to_client_connected():
                self.enclosing_session = SessionStore.instance().addClientConnection(self, message)
            else:
                response = self.enclosing_session.handleMessage(self, message)
                if response is not None:
                    self.sendText(response)
        except Exception as ex:
            print('Exeption handler')
            print(ex)

    def sendText(self, text):
        payload = text.encode('utf8')
        self.sendMessage(payload, isBinary=False)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

class CCCSession:
    """
    CCCSession represents a client client connection with brokering server in between.
    The session lives lives from the moment of the first connect of either app or gis
    to the moment of a connection close.
    Due to security considerations the session is only open a limited time to accept
    a handshaking connection of the later connecting client.
    """
    def __init__(self, session_id):
        self.sessionid = session_id
        self.first_connect = None
        self.giscon = None
        self.appcon = None

    def addClientConnection(self, client_con, method):
        """
        Adds either a connection originating from the application or the gis client
        """
        print('session: add connection. method: ' + method)
        if method == 'appConnect':
            if self.appcon is None:
                self.appcon = client_con
            else:
                raise CCCException('There is already an application connected for this session')
        elif method == 'gisConnect':
            if self.giscon is None:
                self.giscon = client_con
            else:
                raise CCCException('There is already a gis client connected for this session')
        else:
            raise CCCException('Client sent unkown method for initiating client - client connection')

        self.first_connect = datetime.now()
        print('end session.addClientConnection')

    def handleMessage(self, source_con, message):
        destination_con = None
        if source_con is self.appcon:
            destination_con = self.giscon
        else:
            destination_con = self.appcon

        print(destination_con)
        destination_con.sendText(message)
        return None

    def client_to_client_connected(self):
        gis_connected = self.giscon is not None
        app_connected = self.appcon is not None
        return gis_connected and app_connected

class CCCException:
    """Base class for all Exceptions raised in the CCC Server application"""

    def __init__(self, message):
        self.message = message

if __name__ == '__main__':
    import asyncio

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = SocketServerConnection

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '0.0.0.0', 9000)
    server = loop.run_until_complete(coro)

    try:
        print('server starting')
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
