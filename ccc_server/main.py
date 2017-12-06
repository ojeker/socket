"""Entry point to start the server"""
import asyncio
from autobahn.asyncio.websocket import WebSocketServerFactory

import server
import logutil
import config
import urllib.parse

def run_server(server_class):
    logger = logutil.get_baselogger()
    factory = WebSocketServerFactory(config.LISTEN_PATH)
    factory.protocol = server_class

    loop = asyncio.get_event_loop()

    pathparts = urllib.parse.urlparse(config.LISTEN_PATH)
    port = int(pathparts.netloc.split(':')[1])
    coro = loop.create_server(factory, '0.0.0.0', port)
    server = loop.run_until_complete(coro)

    try:
        logger.info(config.SERVER_NAME + ' started; listening on address: ' + config.LISTEN_PATH)
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()

if __name__ == '__main__':
    run_server(server.SocketServerConnection)
