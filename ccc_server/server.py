"""
Contains the classes required to bind to client-server connection together
to a client-server-server-client CCCSession.
The CCC-Session allows for the clients to talk to each other in both directions
"""
from datetime import datetime
from uuid import UUID
import logging

from autobahn.asyncio.websocket import WebSocketServerProtocol

import logutil
import exception

class SessionStore(object):
    """Singleton instance containing all sessions of the corresponding CCCServer"""
    __instance = None

    @staticmethod
    def instance():
        if SessionStore.__instance is None:
            SessionStore.__instance = SessionStore()

        return SessionStore.__instance

    def __init__(self):
        self.session_dict = dict()
        self.log = logutil.get_logger(self)

    def add_connection(self, client_con, message):
        """
        If no session for the given session id exits: Creates a new session and adds it to the dict.
        Calls the sessions addClientConnection() method to ask the session to add the connection
        """
        parts = message.split(':')

        session_id = UUID(parts[0])
        method = parts[1]
        self.log.info('Adding connection with method [{}] to session [{}]'.format(method, session_id))

        session = self.session_dict.get(session_id)
        if session is None:
            session = CCCSession(session_id)
            session.add_connection(client_con, method)
            self.session_dict[session_id] = session
        else:
            session.add_connection(client_con, method)

        return session

    def remove_session(self, session):
        if session.session_id in self.session_dict:
            del self.session_dict[session.session_id]
            self.log.info('Removed session [{}] from store'.format(session.session_id))


class SocketServerConnection(WebSocketServerProtocol):
    """Connection between the ccc_server and one chat client"""

    def __init__(self):
        super().__init__()
        self.enclosing_session = None
        self.client_adr = None
        self.log = logutil.get_logger(self)

    def onConnect(self, request):
        self.client_adr  = request.peer
        self.log.info("Client connecting: {0}".format(self.client_adr))

    def onOpen(self):
        pass

    def onMessage(self, payload, isBinary):
        try:
            if isBinary:
                raise exception.CCCException("Received binary data - should only be text")

            message = payload.decode('utf8').strip()
            self.log.info('message received: ' + message)

            #todo strikte Unterscheidung in "Handshake protokolls" und "CC-Protokolls" damit Handshake protokolls
            #nur genau einmal verwendet werden können.

            if (self.enclosing_session is None or
                    not self.enclosing_session.is_cc_connected()):
                self.enclosing_session = SessionStore.instance().add_connection(self, message)
            else:
                response = self.enclosing_session._forward_message(self, message)
                if response is not None:
                    self.send_text(response)
        except Exception as ex:
            self.log.exception(ex)

            closeReason = CCCSession.CR_APP_PROTOCOLEXCEPTION
            if not isinstance(ex, exception.CCCException):
                closeReason = CCCSession.CR_APP_EXCEPTION

            if self.enclosing_session is not None:
                self.enclosing_session.close(closeReason, channel=self)

    def send_text(self, text):
        payload = text.encode('utf8')
        self.sendMessage(payload, isBinary=False)

    def close(self, reason_code):
        self.enclosing_session = None
        reason_text = CCCSession.close_reasons[reason_code]
        self.sendClose(code=reason_code, reason=reason_text)

    def onClose(self, wasClean, code, reason):
        if code is None or code < 3000:
            if reason is None:
                reason = CCCSession.close_reasons[CCCSession.CR_CHANNEL_CLOSE]
            if self.enclosing_session is not None:
                self.enclosing_session.channel_closed(self)
        else:
            reason = CCCSession.close_reasons[code]
        self.log.info("WebSocket connection to [{}] closed. Reason: {}".format(self.client_adr, reason))

class CCCSession(object):
    """
    CCCSession represents a client client connection with brokering ccc_server in between.
    The session lives lives from the moment of the first connect of either app or gis
    to the moment of a connection close.
    Due to security considerations the session is only open a limited time to accept
    a handshaking connection of the later connecting client.
    """

    #Close reasons (CR) why the session closes
    CR_APP_EXCEPTION = 3000 #General exception causing the session to close
    CR_APP_PROTOCOLEXCEPTION = 3010 #Exception in the application server was raised due to client protocol violation
    CR_CHANNEL_CLOSE = 1000 #The channel to either gis or app client was closed (externally) - causing the session to close

    close_reasons = {
        CR_APP_EXCEPTION: 'General unexpected ccc server exception',
        CR_APP_PROTOCOLEXCEPTION: 'Severe violation of the protocoll through calling client',
        CR_CHANNEL_CLOSE: 'Channel to app or gis client was closed externally'
    }

    def __init__(self, session_id):
        self.session_id = session_id
        self.first_connect = None
        self.giscon = None
        self.appcon = None
        self.log = logutil.get_logger(self)

    def add_connection(self, client_con, method):
        """
        Adds either a connection originating from the application or the gis client
        """
        self.log.info('Adding connection to existing session [{}] by method [{}]'.format(self.session_id, method))
        if method == 'appConnect':
            if self.appcon is None:
                self.appcon = client_con
            else:
                raise exception.CCCException('There is already an application connected for this session')
        elif method == 'gisConnect':
            if self.giscon is None:
                self.giscon = client_con
            else:
                raise exception.CCCException('There is already a gis client connected for this session')
        else:
            raise exception.CCCException('Client sent unkown method for initiating client - client connection')

        if self.is_cc_connected():
            self._emit_ready()
        else:
            self.first_connect = datetime.now()

    def _emit_ready(self):
        """Sends the ready message to both clients"""
        msg = 'ready'
        self.appcon.send_text('ready')
        self.giscon.send_text('ready')

    def _forward_message(self, source_con, message):
        """Forwards the message from ist source connection to the destination connection"""
        destination_con = self._other_channel(source_con)
        destination_con.send_text(message)

        return None

    def is_cc_connected(self):
        """
        Returns true if the handshake between the connections is done, allowing the
        session to forward messages from one connection to the other
        """
        gis_connected = self.giscon is not None
        app_connected = self.appcon is not None
        return gis_connected and app_connected

    def channel_closed(self, source_channel):
        """
        Called from a channel's onClose method if the channel is the source of the
        close.
        After notifying the other channel, removes the channels from the session
        and the session from the session store.
        """
        other = self._other_channel(source_channel)
        if other is not None:
            self._close_channel(other, CCCSession.CR_CHANNEL_CLOSE)

        self._destruct()

    def _destruct(self):
        """Removes the session from the store, removes the channels from the session"""
        SessionStore.instance().remove_session(self)
        self.giscon = None
        self.appcon = None

    def close(self, reason_code):
        """
        Closes the connections of this session and removes the session from the session store
        """
        reason = CCCSession.close_reasons[reason_code]
        self.log.info('Closing session due to reason: {}'.format(reason))

        channels = [self.giscon, self.appcon]
        for channel in channels:
            if channel is not None:
                self._close_channel(channel, reason_code)

        self._destruct()

    def _other_channel(self, channel):
        """Returns the other channel. Example: If the gis channel is given as argument, the app channel is returned"""
        other_channel = None
        if channel is self.giscon:
            other_channel = self.appcon
        elif channel is self.appcon:
            other_channel = self.giscon
        else:
            raise exception.CCCException('Could not identify given channel')

        return other_channel

    def _channel_clienttype(self, channel):
        """Returns the name of the client type of the channel: gisclient or appclient"""
        channel_name = None
        if channel is self.giscon:
            channel_name = 'gisclient'
        elif channel is self.appcon:
            channel_name = 'appclient'
        else:
            raise exception.CCCException('Could not identify given channel')

        return channel_name

    def _close_channel(self, channel, reason_code):
        """Tries to close the given channel. Logs an exception if closing was not possible"""
        try:
            channel.close(reason_code)
        except Exception as ex:
            reason_txt = CCCSession.close_reasons[reason_code]
            channel_name = self._channel_clienttype(channel)
            self.log.exception('Error sending close to {}. Close reason: {}'.format(channel_name, reason_txt))

