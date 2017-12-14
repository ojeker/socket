"""Contains the module, integration and system test for the ccc server"""
import unittest
import client
import util

class TestSystem(unittest.TestCase):

    def ttest_handshake_ok(self):
        """
        Test's the handshaking sequence by subsequently exchanging
        a hello world message
        """
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

    def test_no_session_takeover(self):
        """
        Asserts that a second call to either gisConnect or appConnect
        in the same session fails (preventing session hijacking).
        The calling client receives the corresponding error message.
        """
        server = None
        try:
<<<<<<< HEAD
            #server = util.start_server()

            #clients = [client.GisClient, client.GisHijacker]
            #util.run_clients(clients)
            util.run_client(client.GisClient)
=======
            server = util.start_server()

            clients = [client.GisClient, client.GisHijacker]
            util.run_clients(clients)
>>>>>>> ae99e5bc15851d3a7ac30ec33c6201b659749f28
        finally:
            util.stop_server(server)


if __name__ == '__main__':
    unittest.main()