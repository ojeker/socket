"""Contains the configuration for the server"""

LISTEN_ADDRESS = 'ws://127.0.0.1' #The adress and protocol on which the ccc_server accepts connections
LISTEN_PORT = 9000 #The port on which the ccc_server accepts connections
LISTEN_PATH = 'ws://127.0.0.1:9000'
SERVER_NAME = 'CCC Server' #Name of the Server - Unittests wait on server startup for this name to appear on stdout
ROOTPACKAGE_NAME = 'ccc_server' #name of the package in the project containing the ccc server functionality
