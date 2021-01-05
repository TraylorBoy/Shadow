"""Server instance for the ShadowNetwork"""

import socketserver

class ShadowServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    """TCP Server class"""

    pass
