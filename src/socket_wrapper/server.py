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

    def __init__(self, port: int = 0) -> None:
        """
        Input: port (int) - Port number to bind to, defaults to 0
        Output: None
        Purpose: Initialize server socket and connection
        Description: Sets up server socket, binds to specified port and waits for client
        """
        super().__init__()
        self.__DEBUG = not bool(port)

        self.__port = port
        self.__ip = "127.0.0.1"
        self._serv_sock.bind((self.__ip, self.__port))
        self._serv_sock.listen(100)
        self._sock, addr = self._serv_sock.accept()

    def recv_by_size(self) -> bytes:  # type: ignore
        """
        Input: None
        Output: bytes - Received data from client
        Purpose: Receive data from connected client
        Description: Receives size-prefixed message from the client socket
        """
        return super().recv_by_size(self._sock)

    def send_by_size(self, to_send: bytes) -> None:  # type: ignore
        """
        Input: to_send (bytes) - Data to send to client
        Output: None
        Purpose: Send data to connected client
        Description: Sends size-prefixed message through the client socket
        """
        return super().send_by_size(to_send, self._sock)

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
        elif code == b'HELLO':
            result = self.server_hello()
        elif code == b'REQ':
            result = self.show_stats(fields[1])
        elif code == b'SIGN_UP':
            result = Users.sign_up(*[field.decode() for field in fields[1:]], Users.create_salt())
        elif code == b'SIGN_IN':
            result = Users.check_sign_in(*[field.decode() for field in fields[1:]])
        else:
            result = b'ERR~255'
        return result

    def server_hello(self) -> bytes:
        """
        Input: None
        Output: bytes - Acknowledgment message
        Purpose: Handle initial client greeting
        Description: Returns acknowledgment for client hello message
        """
        return b'ACK'

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
        Description: Closes the client socket connection
        """
        self._sock.close()

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
    test.send_by_size(b'')
