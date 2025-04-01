import socket
import random
import string
import json
from pathlib import Path
from functools import wraps


class Server:

    func_table: dict[bytes, str] = {
        b"code": "corresponding function",
        b"ADD": "add_url",
        b"DEL": "remove_url",
        b"GET": "get_real_url",
    }

    urls_path = f"{Path(__file__).parent.parent}/urls.json"

    def __init__(self, port: int = 0) -> None:
        self.__DEBUG = not bool(port)  # If port == 0 -> debug = true

        self.__ip = "127.0.0.1"  # Host ip
        self.__port = port

        self.__sock = socket.socket()

        self.__sock.bind((self.__ip, self.__port))
        self.__sock.listen(100)

    def recv_by_size(self) -> bytes:
        """Recv message from client, using size field to ensure getting all the message.

        Returns:
            bytes: the message from client without size fields.
            b'': if the client disconnect, or other error occurred.
        """
        msg_size: bytes = b""
        while not b"~" in msg_size:
            msg_size += self.__sock.recv(4)
            if not msg_size:  # msg_size is empty - Client disconnected
                return b""  # Return empty string to indicate the issue

        size_in_bytes, msg = msg_size.split(b"~", 1)
        size = int(size_in_bytes.decode())

        while len(msg) != size:
            msg += self.__sock.recv(128)

        return msg

    def parse(self, data: bytes) -> bytes:
        """Parse data, call apropriate function in Server class.
        Performs the actions required, and return answer according to protocol

        Args:
            data (bytes): data from server

        Returns:
            bytes: answer according to protocol
        """
        fields: list[bytes] = data.split(b"~")

        code: bytes = fields[0]

        result: bytes = eval(f"self.{Server.func_table[code]}(*fields[1:])")
        return result

    def server_hello(self):
        pass

    def show_stats(self):
        pass

    @staticmethod
    def manage_urls(func):
        """Decorator, for managing url files

        Many functions, require retrieving the url dict from the json file, and than after some functionality saving it back.
        This decorator, loads the urls file into a dictionary, than gives it to the function as a parameter. After the function performs its logic, its saves the dict back to the file.
        """

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                with open(Server.urls_path, "r") as f:
                    urls: dict[str, str] = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                urls = {}  # Handle an empty or malformed JSON file

            result = func(self, urls, *args, **kwargs)

            with open(Server.urls_path, "w") as f:
                json.dump(urls, f, indent=4)

            return result

        return wrapper

    @manage_urls
    def add_url(self, urls: dict[str, str], real_url: bytes) -> bytes:
        """Add url to dict.
        Message Format:
        ADD~<real_url>

        Returns:
            b'ACK' (bytes)
        """
        urls[self.generate_fake_url()] = real_url.decode()
        return b"ACK"

    @manage_urls
    def remove_url(self, urls: dict[str, str], fake_url: bytes) -> bytes:
        """Remove url from dict.
        Message format:
        DEL<fake_url>

        Returns:
            b'ACK' (bytes): if operation was completed successfully.
            b'ERR~<function_number>~<error_number> (bytes): If there was an error.
        """
        
        not_found_err_msg = (f"ERR~{list(self.func_table.values()).index('remove_url')}~0")
        val = urls.pop(fake_url.decode(), not_found_err_msg)  # If the url doesn't exist within the url dict, return error msg.
        if "ERR" in val:
            to_return: bytes = val.encode()
        else:
            to_return: bytes = b"ACK"
        return to_return

    @manage_urls
    def get_real_url(self, urls: dict[str, str], fake_url: bytes) -> bytes:
        """Remove url from dict.
        Message format:
        GET<fake_url>

        Returns:
            b'ACK' (bytes): if operation was completed successfully.
            b'ERR~<function_number>~<error_number> (bytes): If there was an error.
        """
        not_found_err_msg = (f"ERR~{list(self.func_table.values()).index('get_real_url')}~0")
        val = urls.get(fake_url.decode(), not_found_err_msg)  # If the url doesn't exist within the url dict, return error msg.
        return val.encode()

    ###### Helper functions - shouldn't be called by instance of the class #########

    def generate_fake_url(self) -> str:
        """Generate a slightly realistic fake URL with a domain and path."""
        tlds = ["com", "net", "org", "info", "biz"]
        words = ["tech","cloud","data","hub","media","net","shop","world","global","secu"]

        random_string = lambda length: "".join(
            random.choices(string.ascii_lowercase, k=length)
        )

        domain = f"{random.choice(words)}{random_string(3)}.{random.choice(tlds)}"
        path = f"/{random.choice(words)}{random_string(2)}/{random_string(4)}"

        return f"https://{domain}.{path}"
