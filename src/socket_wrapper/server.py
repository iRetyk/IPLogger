import sys
import random
import string
import json
import os
from pathlib import Path
from functools import wraps
from typing import Callable


sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from socket_wrapper.network_wrapper import NetworkWrapper
from users import Users


class Server(NetworkWrapper):
    urls_path = f"{Path(__file__).parent.parent}/urls.json"

    def __init__(self, port: int = 0) -> None:
        super().__init__()
        self.__DEBUG = not bool(port)

        self.__ip = "127.0.0.1"
        self.__port = port

        self._sock.bind((self.__ip, self.__port))
        self._sock.listen(100)
        self._sock,addr = self._sock.accept()
    
    def parse(self, data: bytes) -> bytes:
        fields: list[bytes] = data.split(b"~")
        code: bytes = fields[0]
        if code == b'DEL':
            result = self.remove_url(fields[1]) #type:ignore
        elif code == b'GET':
            result = self.get_real_url(fields[1]) #type:ignore
        elif code == b'ADD':
            result = self.add_url(fields[1]) #type:ignore
        elif code == b'HELLO':
            result = self.server_hello(fields[1],fields[2])
        elif code == b'SIGN_UP':
            result = Users.sign_up(*[field.decode() for field in fields[1:]],Users.get_salt(fields[1].decode())) #type:ignore
        elif code == b'SIGN_IN':
            result = Users.check_sign_in(*[field.decode() for field in fields[1:]])
        else:
            result = b'ERR~255'
        return result
    
    def server_hello(self,username,password) -> bytes:
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
    
    
    def cleanup(self):
        self._sock.close()
    
    @manage_urls
    def add_url(self, urls: dict[str, str], real_url: bytes) -> bytes:
        urls[self.generate_fake_url()] = real_url.decode()
        return b"ACK"
    
    @manage_urls
    def remove_url(self, urls: dict[str, str], fake_url: bytes) -> bytes:
        not_found_err_msg = (f"ERR~1~url not found")
        val = urls.pop(fake_url.decode(), not_found_err_msg)
        if "ERR" in val:
            to_return: bytes = val.encode()
        else:
            to_return: bytes = b"ACK"
        return to_return
    
    @manage_urls
    def get_real_url(self, urls: dict[str, str], fake_url: bytes) -> bytes:
        not_found_err_msg = (f"ERR~2~url not found")
        val = urls.get(fake_url.decode(), not_found_err_msg)
        return b'URL~' + val.encode()
    
    def generate_fake_url(self) -> str:
        tlds = ["com", "net", "org", "info", "biz"]
        words = ["tech","cloud","data","hub","media","net","shop","world","global","secu"]

        random_string = lambda length: "".join(
            random.choices(string.ascii_lowercase, k=length)
        )

        domain = f"{random.choice(words)}{random_string(3)}.{random.choice(tlds)}"
        path = f"/{random.choice(words)}{random_string(2)}/{random_string(4)}"

        return f"https://{domain}.{path}"
    

if __name__ == "__main__":
    test = Server()
    test.send_by_size(b'')