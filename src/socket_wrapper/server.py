import sys
import random
import string
import json
import os
import pickle
from socket import socket
from pathlib import Path
from functools import wraps
from typing import Callable


sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from socket_wrapper.network_wrapper import NetworkWrapper
from users import Users

from data.data_helper import fetch_stats

class Server(NetworkWrapper):
    urls_path = f"{Path(__file__).parent.parent}/urls.json"

    def __init__(self, port: int = 0) -> None:
        super().__init__()
        self.__DEBUG = not bool(port)

        self.__ip = "127.0.0.1"
        self.__port = port
        self._serv_sock.bind((self.__ip, self.__port))
        self._serv_sock.listen(100)
        self._sock,addr = self._serv_sock.accept()
    
    def recv_by_size(self) -> bytes: #type:ignore
        return super().recv_by_size(self._sock)
    
    def send_by_size(self, to_send: bytes): #type:ignore
        return super().send_by_size(to_send, self._sock)

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
            result = self.server_hello()
        elif code == b'REQ':
            result = self.show_stats(fields[1])
        elif code == b'SIGN_UP':
            result = Users.sign_up(*[field.decode() for field in fields[1:]],Users.create_salt()) #type:ignore
        elif code == b'SIGN_IN':
            result = Users.check_sign_in(*[field.decode() for field in fields[1:]])
        else:
            result = b'ERR~255'
        return result
    
    def server_hello(self) -> bytes:
        return b'ACK'
    
    def show_stats(self,fake_url: bytes):
        return b'STATS~' + pickle.dumps(fetch_stats(fake_url.decode())) + b'~' + fake_url + b'~' + self.retrieve_url(fake_url).encode() + b'\n\n' #type:ignore
    
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
    def retrieve_url(self,urls: dict[str,str],fake_url: bytes) -> str:
        return urls.get(fake_url.decode(),"<real_url_here> (debug)")
    
    
    @manage_urls
    def add_url(self, urls: dict[str, str], real_url: bytes) -> bytes:
        fake_url = self.generate_fake_url()
        urls[fake_url] = real_url.decode()
        return f"URL~{fake_url}".encode()
    
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