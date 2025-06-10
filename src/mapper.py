import json
import threading
import socket

from typing import Dict, Optional

SERVER_IP = "10.68.121.147"

class ClientMapper:
    """Class for mapping client IPs to their requested domains with thread-safe operations."""

    def __init__(self,dns_process: bool = False) -> None:
        """
        Input: None
        Output: None
        Purpose: Initialize the client mapper
        Description: Creates an empty map and initializes thread lock for synchronization
        """
        self.__map: Dict[str, str] = {}
        
        if dns_process:
            print("Recieved dns process")
            self.__sock = socket.socket()
            self.__sock.bind(("127.0.0.1",4444))
            self.__sock.listen(2)
            self.__sock,_ = self.__sock.accept()
            self.__answer_thread: threading.Thread = threading.Thread(target=self.handle_request,daemon=True)
            self.__answer_thread.start()
        else:
            print("Recieved http process")
            self.__sock = socket.socket()
            self.__sock.connect(("127.0.0.1",4444))


        
    
    def handle_request(self):
        while True:
            message: bytes = self.__sock.recv(64)

            ip = message.decode()
            print(f"Redirecting {ip} to {self.__map.get(ip,'a non existent ip')}")
            self.__sock.send(self.__map.pop(ip,"www.default.com").encode())
            
            
    
    def add_client(self, ip: str, domain: str) -> None:
        """
        Input: ip (str) - Client IP address, domain (str) - Domain requested by client
        Output: None
        Purpose: Add or update client mapping
        Description: Maps a client IP to their requested domain in a thread-safe manner
        """
        self.__map[ip] = domain
        log(f"Added ip {ip} to map - {domain = }")

    def get_domain(self, ip: str) -> str:
        """
        Input: ip (str) - Client IP address to look up
        Output: str - Domain associated with the IP
        Purpose: Retrieve and remove domain mapping for an IP
        Description: Gets and removes the domain mapping for a client IP, returning default if not found
        """
        
        if ip == "127.0.0.1":
            ip = SERVER_IP
        
        self.__sock.send(ip.encode())
        log("Retrieved domainn name for " + str(ip))
        return self.__sock.recv(256).decode()


def log(to_log):
    with open('log.txt', 'a') as f:
        f.writelines([to_log])