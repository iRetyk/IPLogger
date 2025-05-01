import socket


class NetworkWrapper:
    """
    Father class of Server and Client. contains all common attirbutes, which are all networking related. this is the only class that creates socket objects.
    """
    def __init__(self) -> None:
        self._serv_sock = socket.socket()
        self._serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def recv_by_size(self,sock = None) -> bytes:
        """Recv message from client, using size field to ensure getting all the message.

        Returns:
            bytes: the message from client without size fields.
            b'': if the client disconnects, or other error occurred.
        """
        if sock is None:
            sock = self._serv_sock
        
        msg_size: bytes = b""
        while not b"~" in msg_size:
            msg_size += sock.recv(1)
            if not msg_size:  # msg_size is empty - Client disconnected
                return b""  # Return empty string to indicate the issue

        size_in_bytes, msg = msg_size.split(b"~", 1)
        size = int(size_in_bytes.decode())

        while len(msg) != size:
            msg += sock.recv(128)
        
        # log
        print("Received >>>" + str(msg))
        return msg
    
    
    def send_by_size(self, to_send: bytes,sock = None):
        
        if sock is None:
            sock = self._serv_sock
        
        to_send = str(len(to_send)).encode() + b'~' + to_send
        print(" Sending>>>>> " + str(to_send)[2:-1])
        sock.send(to_send)
