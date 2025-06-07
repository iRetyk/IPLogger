import socket
from typing import Optional, Union

from encryptions import AES_encrypt,AES_decrypt

class NetworkWrapper:
    """Base class for Server and Client with common networking functionality."""

    def __init__(self) -> None:
        """
        Input: None
        Output: None
        Purpose: Initialize network socket
        Description: Creates and configures a socket with address reuse enabled and timeout
        """
        self._serv_sock = socket.socket()
        self._serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Set a timeout to allow for clean interruption
        self._serv_sock.settimeout(1.0)

    def recv_by_size(self, key: Optional[bytes] = None, sock: Optional[socket.socket] = None,encrypted: bool = True) -> bytes:
        """
        Input: sock (Optional[socket.socket]) - Socket to receive from, uses default if None
        Output: bytes - Received message without size fields or empty bytes if disconnected
        Purpose: Receive size-prefixed message from socket
        Description: Receives a message using size field to ensure complete message receipt,
                    handles disconnection and error cases
        """
        if sock is None:
            sock = self._serv_sock

        try:
            if encrypted:
                iv = sock.recv(16)
                if not iv:
                    return b''
                
                while not b'|' in iv:
                    iv += sock.recv(4)
                
                parts = iv.split(b'|')
                iv,msg_size = parts
            else:
                msg_size: bytes = b''
            while b"~" not in msg_size:
                chunk = sock.recv(1)
                if not chunk:  # Client disconnected
                    return b""
                msg_size += chunk

            size_in_bytes, msg = msg_size.split(b"~", 1)
            size = int(size_in_bytes.decode())

            while len(msg) != size:
                msg += sock.recv(128)
                
        except socket.timeout:
            return b""  # Return empty on timeout to allow for clean interruption

        if encrypted: 
            plain_msg = AES_decrypt(key,iv,msg) #type:ignore
        else:
            plain_msg = msg
        
        print("Received >>>" + str(plain_msg)[2:-1])
        return plain_msg

    def send_by_size(self, to_send: bytes,key: Optional[bytes] = None, sock: Optional[socket.socket] = None,encrypted:bool = True) -> None:
        """
        Input: to_send (bytes) - Data to send, sock (Optional[socket.socket]) - Socket to send through
        Output: None
        Purpose: Send size-prefixed message through socket
        Description: Prepends message size to data and sends through specified socket
        """
        if sock is None:
            sock = self._serv_sock
        if encrypted:
            iv,cipher = AES_encrypt(key,to_send) #type:ignore
            bytearray_data: bytes = str(len(cipher)).encode() + b'~' + cipher
            
            final_to_send :bytes = iv + b'|' + bytearray_data #type:ignore
        else:
            final_to_send = str(len(to_send)).encode() + b'~' + to_send
        print(" Sending>>>>> " + str(final_to_send)[2:-1])
        sock.send(final_to_send)
