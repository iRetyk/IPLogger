import sys
import random
import string
import json
import os
import pickle

from socket import socket
from pathlib import Path
from functools import wraps
from typing import Any, Dict, List, Callable, Optional, TypeVar, cast

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from socket_wrapper.network_wrapper import NetworkWrapper
from users import Users
from data.data_helper import fetch_stats

from encryptions import generate_keys_RSA, RSA_decrypt

T = TypeVar('T')
UrlDict = Dict[str, str]

def manage_urls(func: Callable[..., T]) -> Callable[..., T]:
    """
    Input: func (Callable) - Function to be decorated
    Output: Callable - Wrapped function with URL management
    Purpose: Decorator for URL management operations
    Description: Manages loading and saving of URLs file for URL operations
    """
    @wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> T:
        try:
            with open(Server.urls_path, "r") as f:
                urls = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            urls = {}

        result = func(self, urls, *args, **kwargs)

        with open(Server.urls_path, "w") as f:
            json.dump(urls, f, indent=4)

        return result

    return wrapper

class Server(NetworkWrapper):
    """Server class for handling URL management and client requests."""

    urls_path = f"{Path(__file__).parent.parent.parent}/urls.json"

    def __init__(self, ip: str = "127.0.0.1", port: int = 0) -> None:
        """
        Input: port (int) - Port number to bind to, defaults to 0
        Output: None
        Purpose: Initialize server socket
        Description: Sets up server socket and binds to specified port
        """
        super().__init__()
        self.__DEBUG = not bool(port)
        self.__port = port
        self.__ip = ip
        self.init_encryptions()
        self._serv_sock.bind((self.__ip, self.__port))
        self._serv_sock.listen(100)


    def init_encryptions(self):
        self.__RSA_private, self.__RSA_public = generate_keys_RSA()
    
    def recv_by_size(self,key: Optional[bytes]= None, sock: Optional[socket] = None, encrypted: bool = True) -> bytes:
        """
        Input: sock (Optional[socket]) - Client socket to receive from
        Output: bytes - Received data from client
        Purpose: Receive data from specified client
        Description: Uses parent class's recv_by_size with specified socket
        """
        return super().recv_by_size(key,sock,encrypted)

    def send_by_size(self, to_send: bytes,key :Optional[bytes] = None, sock: Optional[socket] = None, encrypted: bool = True) -> None:
        """
        Input:  to_send (bytes) - Data to send to client
                sock (Optional[socket]) - Client socket to send to
        Output: None
        Purpose: Send data to specified client
        Description: Uses parent class's send_by_size with specified socket
        """
        return super().send_by_size(to_send, key,sock,encrypted)

    
    def exchange_keys(self, sock: socket) -> bytes:
            """
            swaps with client keys for AES using RSA
            first the server sends public key, than client sends AES key encrypted using the public key, than server decrypts the AES key. Handshake done
            

            Args:
                sock (socket): the socket

            Returns:
                bytes: AES key
            """
            
            self.send_by_size(self.__RSA_public,sock=sock,encrypted=False)
            enc_key = self.recv_by_size(sock=sock,encrypted=False)

            AES_key = RSA_decrypt(self.__RSA_private,enc_key)
            
            print("Received AES key:",AES_key)
            return AES_key

    
    def parse(self, data: bytes) -> bytes:
        """
        Input: data (bytes) - Raw data received from client
        Output: bytes - Response to send back to client
        Purpose: Parse and handle client requests
        Description: Interprets client commands and calls appropriate handlers
        """
        fields: List[bytes] = data.split(b"~")
        code: bytes = fields[0]
        if code == b'DEL':
            result = self.remove_url(fields[1])
        elif code == b'GET':
            result = self.get_real_url(fields[1])
        elif code == b'ADD':
            result = self.add_url(fields[1])
        elif code == b'REQ':
            result = self.show_stats(fields[1])
        elif code == b'SIGN_UP':
            result = Users.sign_up(*[field.decode() for field in fields[1:]], Users.create_salt())
        elif code == b'SIGN_IN':
            result = Users.check_sign_in(*[field.decode() for field in fields[1:]])
        else:
            result = b'ERR~255'
        return result

    def show_stats(self, fake_url: bytes) -> bytes:
        """
        Input: fake_url (bytes) - URL to get statistics for
        Output: bytes - Formatted statistics response
        Purpose: Retrieve access statistics for URL
        Description: Fetches and formats URL access statistics
        """
        d = fetch_stats(fake_url.decode())
        if d is None:  # url doesn't exist
            return b'ERR~4~Url Not Found'
        real_url = self.retrieve_url(fake_url)
        return b'STATS~' + pickle.dumps(d) + b'~' + fake_url + b'~' + real_url.encode()

    def cleanup(self) -> None:
        """
        Input: None
        Output: None
        Purpose: Clean up server resources
        Description: Closes the server socket
        """
        self._serv_sock.close()

    @manage_urls
    def retrieve_url(self, urls: UrlDict, fake_url: bytes) -> str:
        """
        Input: urls (UrlDict) - URL mappings, fake_url (bytes) - URL to look up
        Output: str - Real URL or debug message
        Purpose: Get real URL for given fake URL
        Description: Retrieves the real URL mapped to the given fake URL
        """
        return urls.get(fake_url.decode(), "<real_url_here> (debug)")

    @manage_urls
    def add_url(self, urls: UrlDict, real_url: bytes) -> bytes:
        """
        Input: urls (UrlDict) - URL mappings, real_url (bytes) - URL to add
        Output: bytes - Response with generated fake URL
        Purpose: Add new URL mapping
        Description: Generates fake URL and creates mapping to real URL
        """
        fake_url = self.generate_fake_url()
        urls[fake_url] = real_url.decode()
        return f"URL~{fake_url}".encode()

    @manage_urls
    def remove_url(self, urls: UrlDict, fake_url: bytes) -> bytes:
        """
        Input: urls (UrlDict) - URL mappings, fake_url (bytes) - URL to remove
        Output: bytes - Success or error message
        Purpose: Remove URL mapping
        Description: Removes mapping for given fake URL if it exists
        """
        not_found_err_msg = "ERR~1~url not found"
        val = urls.pop(fake_url.decode(), not_found_err_msg)
        if "ERR" in val:
            return val.encode()
        return b"ACK"

    @manage_urls
    def get_real_url(self, urls: UrlDict, fake_url: bytes) -> bytes:
        """
        Input: urls (UrlDict) - URL mappings, fake_url (bytes) - URL to look up
        Output: bytes - Real URL or error message
        Purpose: Get real URL for fake URL
        Description: Retrieves real URL mapped to given fake URL
        """
        not_found_err_msg = "ERR~2~url not found"
        val = urls.get(fake_url.decode(), not_found_err_msg)
        return b'URL~' + val.encode()

    def generate_fake_url(self) -> str:
        """
        Input: None
        Output: str - Generated fake URL
        Purpose: Generate new fake URL
        Description: Creates random fake URL using predefined components
        """
        tlds = ["com", "net", "org", "info", "biz"]
        words = ["tech", "cloud", "data", "hub", "media", "net", "shop", "world", "global", "secu"]

        random_string = lambda length: "".join(
            random.choices(string.ascii_lowercase, k=length)
        )

        domain = f"{random.choice(words)}{random_string(3)}{random.choice(tlds)}"
        path = f"/{random.choice(words)}{random_string(2)}/{random_string(4)}"

        return f"https://{domain}"

if __name__ == "__main__":
    test = Server()
    
