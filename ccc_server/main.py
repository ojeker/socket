"""Entry point to start the server"""
import asyncio
import urllib.parse

from autobahn.asyncio.websocket import WebSocketServerFactory

import server
from ccc_server import logutil
from ccc_server import config

def run_server(server_class):
    """Starts the server"""
    logger = logutil.get_baselogger()
    factory = WebSocketServerFactory(config.LISTEN_PATH)
    factory.protocol = server_class

    loop = asyncio.get_event_loop()

    pathparts = urllib.parse.urlparse(config.LISTEN_PATH)
    port = int(pathparts.netloc.split(':')[1])
    coro = loop.create_server(factory, '0.0.0.0', port)
    sockserver = loop.run_until_complete(coro)

    try:
        logger.info(config.SERVER_NAME + ' started; listening on address: ' + config.LISTEN_PATH)
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        sockserver.close()
        loop.close()

if __name__ == '__main__':
    run_server(server.SocketServerConnection)
