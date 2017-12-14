"""Main program"""

import asyncio
import concurrent.futures
from autobahn.asyncio.websocket import WebSocketClientFactory

def add_server_to_path():
    """Adds the ccc_server package to the pythonpath"""
    testpath = pathlib.Path(os.path.abspath(__file__))
    basepath = testpath.parents[1] #relative to up
    serverpath = os.path.join(basepath, 'ccc_server')

    if serverpath not in sys.path:
        sys.path.append(serverpath)


import client
import os.path
import sys
import pathlib
import urllib.parse
import time

import pexpect

add_server_to_path()
import config
import testconfig


def start_server():
    """
    Starts the server that will be tested by the integration tests.
    Makes sure that the server is ready to accept connections before returning.

    Returns the handle to the serverprocess (to be able to stop the process after the tests)
    """
    child = pexpect.spawn(testconfig.TESTRUN_PATH_PYTHON, [testconfig.TESTRUN_PATH_SERVERMODULE])

    foundidx = -1
    sleepmillis = 3
    for i in range(5):
        if foundidx > -1:
            break

        try:
            time.sleep(sleepmillis/1000)
            foundidx = child.expect('.*({})'.format(config.SERVER_NAME))
        except Exception as ex:
            print('server not ready ' + str(child))
        finally:
            sleepmillis = sleepmillis**2


    return child

def stop_server(serverhandle):
    """
    Stops the ccc_server using the given serverhandle.

    The serverhandle is the returnvalue of pexpect.spawn(..)
    """
    if serverhandle is not None:
        clean_end = serverhandle.terminate(force=False)
        if not clean_end:
            serverhandle.terminate(force=True)

def run_client(client_class):
    """
    Runs the given client until the client himself calls close or an exception is thrown.
    Is non blocking to allow the interaction of the gis and app client.
    """
    result = None

    try:
        pathparts = urllib.parse.urlparse(config.LISTEN_PATH)
        adrparts = pathparts.netloc.split(':')

        factory = WebSocketClientFactory(config.LISTEN_PATH)
        factory.protocol = client_class

        loop = asyncio.get_event_loop()
        coro = loop.create_connection(
            factory, adrparts[0], adrparts[1])
        loop.run_until_complete(coro)
        loop.run_forever()
        loop.close()
    except Exception as ex:
        result = ex

    return result

def run_clients(client_list):
    with concurrent.futures.ProcessPoolExecutor(2) as executor:
        results = executor.map(run_client, client_list)

    for res in results:
        print(res)


if __name__ == '__main__':
    run_client(client.AppClient)

