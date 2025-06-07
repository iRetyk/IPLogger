import pickle
from typing import Dict, List, Tuple, Any, TypedDict

from socket_wrapper.network_wrapper import NetworkWrapper
from encryptions import generate_AES_key,RSA_encrypt

class PacketData(TypedDict):
    IP: str
    Time: str

class Client(NetworkWrapper):
    """Client class that handles socket communication with the server."""

    def __init__(self, ip: str, port: int) -> None:
        """
        Input: ip (str) - server IP address, port (int) - server port number
        Output: None
        Purpose: Initialize client socket and connect to server
        Description: Creates a socket connection to the specified server IP and port
        """
        super().__init__()
        self.__ip = ip
        self.__port = port
        self.__AES_key = None
        self._serv_sock.connect((self.__ip, self.__port))

    def recv_by_size(self) -> bytes:  # type: ignore
        """
        Input: None
        Output: bytes - received data from server
        Purpose: Receive data from the server
        Description: Receives data from server using the parent class's receive method
        """
        return super().recv_by_size(self.__AES_key, self._serv_sock)

    def send_by_size(self,to_send: bytes,key = None) -> None:  # type: ignore
        """
        Input: to_send (bytes) - data to send to server
        Output: None
        Purpose: Send data to the server
        Description: Sends data to server using the parent class's send method
        """
        return super().send_by_size(to_send,self.__AES_key, self._serv_sock)

    def exchange_keys(self):
        """
        swaps with server keys for AES using RSA
        first the server sends public key, than clinet sends AES key encrypted using the public key, than server decrypts the AES key. Handshake done
        """
        
        self.__AES_key = generate_AES_key()

        server_key = self.recv_by_size()
        self.send_by_size(RSA_encrypt(server_key,self.__AES_key),self.__AES_key)
        print("Sent AES key: ", self.__AES_key)
    
    
    def parse(self, from_server: bytes) -> Tuple[str, str]:
        """
        Input: from_server (bytes) - message from server
        Output: tuple(str, str) - message to show user and message type (error/success)
        Purpose: Parse server response messages
        Description: Decodes and interprets server responses into user-friendly messages
        """
        fields = from_server.split(b'~')
        code = fields[0]

        if code == b'':
            return "", ""
        elif code == b'ACK':
            return "Action was done successfully", "success"
        elif code == b'STATS':
            data: List[PacketData] = pickle.loads(fields[1])
            fake_url = fields[2]
            real_url = fields[3]
            return self.format_data(data, fake_url.decode(), real_url.decode()), "success"
        elif code == b'URL':
            return f"Url - {fields[1].decode()}", "success"
        elif code == b'ERR':
            return f"Action failed - {fields[2].decode()}", "error"
        else:
            raise Exception("Unknown code")

    def client_hello(self) -> bytes:
        """
        Input: None
        Output: bytes - hello message
        Purpose: Create initial hello message
        Description: Returns the client's hello message for server handshake
        """
        return b'HELLO'

    def cleanup(self) -> None:
        """
        Input: None
        Output: None
        Purpose: Clean up client resources
        Description: Closes the socket connection to the server
        """
        self._serv_sock.close()

    def format_data(self, data: List[PacketData], fake: str, real: str) -> str:
        """
        Input: data (list) - list of entries, fake (str) - fake URL, real (str) - real URL
        Output: str - formatted string containing the data
        Purpose: Format URL statistics data for display
        Description: Creates a human-readable string from the URL statistics data
        """
        st = "Entries recorded for " + fake + f"({real})\n\n"
        for i, d in enumerate(data):
            st += f"Entry No. {i}\n"
            for k, v in d.items():
                st += f" - - - - - {k} : {v}\n"
            st += "\n"
        return st

    def sign_up(self, username: str, password: str, cpassword: str, err: str = "") -> bytes:
        """
        Input: username (str) - user's username, password (str) - user's password,
               cpassword (str) - confirmation password, err (str) - error message
        Output: bytes - formatted signup request
        Purpose: Create signup request message
        Description: Formats and encodes a signup request for the server
        """
        return f"SIGN_UP~{username}~{password}~{cpassword}".encode()

    def login(self, username: str, password: str, err: str = "") -> bytes:
        """
        Input: username (str) - user's username, password (str) - user's password,
               err (str) - error message
        Output: bytes - formatted login request
        Purpose: Create login request message
        Description: Formats and encodes a login request for the server
        """
        return f"SIGN_IN~{username}~{password}".encode()

    def add_url(self, url: str, err: str = "") -> bytes:
        """
        Input: url (str) - URL to add, err (str) - error message
        Output: bytes - formatted add URL request
        Purpose: Create URL addition request
        Description: Formats and encodes a request to add a new URL to the system
        """
        return f"ADD~{url}".encode()

    def remove_url(self, fake_url: str, err: str = "") -> bytes:
        """
        Input: fake_url (str) - fake URL to remove, err (str) - error message
        Output: bytes - formatted remove URL request
        Purpose: Create URL removal request
        Description: Formats and encodes a request to remove a URL from the system
        """
        return f"DEL~{fake_url}".encode()

    def get_real_url(self, fake_url: str, err: str = "") -> bytes:
        """
        Input: fake_url (str) - fake URL to look up, err (str) - error message
        Output: bytes - formatted get real URL request
        Purpose: Create request to get original URL
        Description: Formats and encodes a request to get the real URL for a fake URL
        """
        return f"GET~{fake_url}".encode()

    def req_info(self, fake_url: str, err: str = "") -> bytes:
        """
        Input: fake_url (str) - fake URL to get info for, err (str) - error message
        Output: bytes - formatted request info request
        Purpose: Create request to get URL information
        Description: Formats and encodes a request to get statistics/info for a fake URL
        """
        return f"REQ~{fake_url}".encode()
