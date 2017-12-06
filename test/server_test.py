"""Contains the module, integration and system test for the ccc server"""
import unittest
import client
import util

class TestSystem(unittest.TestCase):

    def test_handshake_ok(self):
        child = None
        try:
            child = util.start_server()

            clients = [client.AppClient, client.GisClient]
            util.run_clients(clients)
        finally:
            if child is not None:
                clean_end = child.terminate(force=False)
                if not clean_end:
                    child.terminate(force=True)

if __name__ == '__main__':
    unittest.main()