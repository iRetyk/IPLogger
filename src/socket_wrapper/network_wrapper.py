import socket
from typing import Optional, Union

class NetworkWrapper:
    """Base class for Server and Client with common networking functionality."""

    def __init__(self) -> None:
        """
        Input: None
        Output: None
        Purpose: Initialize network socket
        Description: Creates and configures a socket with address reuse enabled
        """
        self._serv_sock = socket.socket()
        self._serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def recv_by_size(self, sock: Optional[socket.socket] = None) -> bytes:
        """
        Input: sock (Optional[socket.socket]) - Socket to receive from, uses default if None
        Output: bytes - Received message without size fields or empty bytes if disconnected
        Purpose: Receive size-prefixed message from socket
        Description: Receives a message using size field to ensure complete message receipt,
                    handles disconnection and error cases
        """
        if sock is None:
            sock = self._serv_sock

        msg_size: bytes = b""
        while b"~" not in msg_size:
            chunk = sock.recv(1)
            if not chunk:  # Client disconnected
                return b""
            msg_size += chunk

        size_in_bytes, msg = msg_size.split(b"~", 1)
        size = int(size_in_bytes.decode())

        while len(msg) != size:
            msg += sock.recv(128)

        print("Received >>>" + str(msg)[2:-1])
        return msg

    def send_by_size(self, to_send: bytes, sock: Optional[socket.socket] = None) -> None:
        """
        Input: to_send (bytes) - Data to send, sock (Optional[socket.socket]) - Socket to send through
        Output: None
        Purpose: Send size-prefixed message through socket
        Description: Prepends message size to data and sends through specified socket
        """
        if sock is None:
            sock = self._serv_sock

        to_send = str(len(to_send)).encode() + b'~' + to_send
        print(" Sending>>>>> " + str(to_send)[2:-1])
        sock.send(to_send)
