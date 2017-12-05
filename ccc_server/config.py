"""Contains the configuration for the server"""

LISTEN_ADDRESS = 'ws://127.0.0.1' #The adress and protocol on which the ccc_server accepts connections
LISTEN_PORT = 9000 #The port on which the ccc_server accepts connections
ROOTPACKAGE_NAME = 'ccc_server' #the name of the root package (directory name) - could not find good way to find out dynamically