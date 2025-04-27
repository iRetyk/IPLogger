import socket


class NetworkWrapper:
    """
    Father class of Server and Client. contains all common attirbutes, which are all networking related. this is the only class that creates socket objects.
    """
    def __init__(self) -> None:
        self._sock = socket.socket()
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def recv_by_size(self) -> bytes:
        """Recv message from client, using size field to ensure getting all the message.

        Returns:
            bytes: the message from client without size fields.
            b'': if the client disconnects, or other error occurred.
        """
        msg_size: bytes = b""
        while not b"~" in msg_size:
            msg_size += self._sock.recv(4)
            if not msg_size:  # msg_size is empty - Client disconnected
                return b""  # Return empty string to indicate the issue

        size_in_bytes, msg = msg_size.split(b"~", 1)
        size = int(size_in_bytes.decode())

        while len(msg) != size:
            msg += self._sock.recv(128)
        
        # log
        print("Received >>>" + msg.decode())
        return msg

    def send_by_size(self, to_send: bytes):
        to_send = f'{len(to_send)}~{to_send.decode()}'.encode()
        print(" Sending>>>>> " + to_send.decode())
        self._sock.send(to_send)
