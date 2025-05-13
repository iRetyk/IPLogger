from threading import Lock
import json


SERVER_IP = "10.68.121.52"


class ClientMapper:
    def __init__(self):
        self.__map: dict[str,str] = {}
        self.__lock = Lock()
    
    def add_client(self,ip: str, domain: str):
        self.get_map()
        with self.__lock:
            self.__map[ip] = domain
        self.save_map()
    
    def get_domain(self,ip: str):
        self.get_map()
        if ip == "127.0.0.1":
             ip = SERVER_IP
        with self.__lock:
            to_return =  self.__map.pop(ip,"www.default.com")
        self.save_map()
        return to_return

    def get_map(self):
        with self.__lock:
            try:
                with open('map.json','r') as f:
                    self.__map = json.load(f)
            except json.JSONDecodeError:
                self.__map = {}
            except FileNotFoundError:
                self.__map = {}
    
    def save_map(self):
        with self.__lock:
            with open('map.json','w') as f:
                json.dump(self.__map,f)