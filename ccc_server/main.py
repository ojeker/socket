"""Entry point to start the server"""
import asyncio
from autobahn.asyncio.websocket import WebSocketServerFactory

import server
import logutil
import config

if __name__ == '__main__':
    logger = logutil.get_baselogger()
    adr = config.LISTEN_ADDRESS + ':' + str(config.LISTEN_PORT)
    factory = WebSocketServerFactory(adr)
    factory.protocol = server.SocketServerConnection

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '0.0.0.0', config.LISTEN_PORT)
    server = loop.run_until_complete(coro)

    try:
        logger.info('Server started; listening on address: ' + adr)
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()