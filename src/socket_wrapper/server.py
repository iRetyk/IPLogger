import socket
import random
import string
import json
from pathlib import Path
from functools import wraps
from typing import Callable

from .network_wrapper import NetworkWrapper



class Server(NetworkWrapper):
    urls_path = f"{Path(__file__).parent.parent}/urls.json"

    def __init__(self, port: int = 0) -> None:
        super().__init__()
        self.__DEBUG = not bool(port)

        self.__ip = "127.0.0.1"
        self.__port = port

        self._sock.bind((self.__ip, self.__port))
        self._sock.listen(100)
    
    def parse(self, data: bytes) -> bytes:
        fields: list[bytes] = data.split(b"~")
        code: bytes = fields[0]
        result: bytes = Server.func_table[code](*fields[1:])
        return result
    
    def server_hello(self) -> bytes:
        return b'ACK'
    
    def show_stats(self):
        pass
    
    @staticmethod
    def manage_urls(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                with open(Server.urls_path, "r") as f:
                    urls: dict[str, str] = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                urls = {}
            
            result = func(self, urls, *args, **kwargs)
            
            with open(Server.urls_path, "w") as f:
                json.dump(urls, f, indent=4)

            return result
        
        return wrapper
    
    @manage_urls
    def add_url(self, urls: dict[str, str], real_url: bytes) -> bytes:
        urls[self.generate_fake_url()] = real_url.decode()
        return b"ACK"
    
    @manage_urls
    def remove_url(self, urls: dict[str, str], fake_url: bytes) -> bytes:
        not_found_err_msg = (f"ERR~{list(self.func_table.values()).index(self.remove_url)}~0")
        val = urls.pop(fake_url.decode(), not_found_err_msg)
        if "ERR" in val:
            to_return: bytes = val.encode()
        else:
            to_return: bytes = b"ACK"
        return to_return
    
    @manage_urls
    def get_real_url(self, urls: dict[str, str], fake_url: bytes) -> bytes:
        not_found_err_msg = (f"ERR~{list(self.func_table.values()).index(self.get_real_url)}~0")
        val = urls.get(fake_url.decode(), not_found_err_msg)
        return val.encode()
    
    def generate_fake_url(self) -> str:
        tlds = ["com", "net", "org", "info", "biz"]
        words = ["tech","cloud","data","hub","media","net","shop","world","global","secu"]

        random_string = lambda length: "".join(
            random.choices(string.ascii_lowercase, k=length)
        )

        domain = f"{random.choice(words)}{random_string(3)}.{random.choice(tlds)}"
        path = f"/{random.choice(words)}{random_string(2)}/{random_string(4)}"

        return f"https://{domain}.{path}"
    
    func_table: dict[bytes,Callable] = {
        b"ADD": add_url,
        b"DEL": remove_url,
        b"GET": get_real_url,
        b"HELLO": server_hello
    }


test = Server()
test.send_by_size(b'')