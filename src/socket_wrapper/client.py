import socket

class Client:
    def __init__(self,ip: str,port: int) -> None:
        self.__ip = ip
        self.__port = port

        self.__sock = socket.socket()
        
        self.__sock.connect((self.__ip,self.__port))
    
    
    def menu(self) -> int:
        # Input a number from user
        # According to choice go to matching function.
        # 1 - add
        # 2 - get
        # 3 - remove
        # 4 - get info
        raise NotImplementedError
    
    def client_hello(self):
        pass
    
    def add_url(self, real_url: str):
        # Input from user the url.
        # Than build and return the request.
        pass
    
    def remove_url(self, url: str):
        # No need for further input.
        # Build and return the request.
        pass
    
    def req_info(self, url):
        # Input from user the url.
        # Than build and return the request.
        pass
    
    