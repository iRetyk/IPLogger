import socket


class Client:
    def __init__(self,ip: str,port: int) -> None:
        self.__ip = ip
        self.__port = port

        self.__sock = socket.socket()
        
        self.__sock.connect((self.__ip,self.__port))
        