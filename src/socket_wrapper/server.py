import socket


class Server:
    def __init__(self,port: int) -> None:
        self.__ip = "127.0.0.1" # Host ip
        self.__port = port
        
        self.__sock = socket.socket()
        
        self.__sock.bind((self.__ip,self.__port))
        self.__sock.listen(100)
        