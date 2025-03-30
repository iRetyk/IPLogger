import socket

class Client:
    def __init__(self,ip: str,port: int) -> None:
        self.__ip = ip
        self.__port = port

        self.__sock = socket.socket()
        
        self.__sock.connect((self.__ip,self.__port))
    
    
    def parse(self, data: bytes):
        pass
    
    def client_hello(self):
        pass
    
    def add_url(self, read_url: str):
        pass
    
    def remove_url(self, url: str):
        pass
    
    def req_info(self, url):
        """
        request server for stats about a specific url
        """
        pass
    
    