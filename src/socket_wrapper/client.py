import sys
import os
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))
from socket_wrapper.network_wrapper import NetworkWrapper
#from ...ui import app

# Make cwd project/
os.chdir(Path(__file__).resolve().parent.parent.parent)

class Client(NetworkWrapper):
    def __init__(self, ip: str, port: int) -> None:
        super().__init__()
        self.__ip = ip
        self.__port = port

        self._serv_sock.connect((self.__ip, self.__port))
    
    
    def recv_by_size(self) -> bytes: #type:ignore
        return super().recv_by_size(self._serv_sock)
    
    def send_by_size(self, to_send: bytes): #type:ignore
        return super().send_by_size(to_send, self._serv_sock)
    
    def parse(self, from_server: bytes) -> bytes:
        """Parse server response

        Args:
            from_server (bytes): message from server

        Raises:
            Exception: if uknown message

        Returns:
            bytes: message from server.
        """
        fields = from_server.split(b'~')
        code = fields[0]
        
        if code == b'':
            return b''
        elif code == b'ACK':
            return b''
        elif code == b'STATS':
            self.display_stats(fields[1:])
            return b''
        elif code == b'URL':
            self.display_url(fields[1].decode())
            return b''
        elif code == b'ERR':
            return from_server
        else:
            raise Exception("Unknown code")
    
    

    def client_hello(self) -> bytes:
        return b'HELLO'

    
    
    def cleanup(self):
        self._serv_sock.close()
    
    def sign_up(self, username: str, password: str, cpassword: str, err: str = "") -> bytes:
        # Return formatted request for sign-up
        return f"SIGN_UP~{username}~{password}~{cpassword}".encode()

    def login(self, username: str, password: str, err: str = "") -> bytes:
        # Return formatted request for login
        return f"SIGN_IN~{username}~{password}".encode()

    def add_url(self, fake_url: str, err: str = "") -> bytes:
        # Return formatted request to add a URL
        return f"ADD~{fake_url}".encode()

    def remove_url(self, fake_url: str, err: str = "") -> bytes:
        # Return formatted request to remove a URL
        return f"DEL~{fake_url}".encode()

    def get_real_url(self, fake_url: str, err: str = "") -> bytes:
        # Return formatted request to get the real URL
        return f"GET~{fake_url}".encode()

    def req_info(self, fake_url: str, err: str = "") -> bytes:
        # Return formatted request to fetch request info
        return f"REQ~{fake_url}".encode()

    def display_url(self, url: str):
        # Simple passthrough for Flask template rendering
        return url

    def display_stats(self, *args):
        # Not implemented yet
        raise NotImplementedError