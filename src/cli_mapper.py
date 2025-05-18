import json
from threading import Lock
from typing import Dict, Optional

SERVER_IP = "10.68.121.52"

class ClientMapper:
    """Class for mapping client IPs to their requested domains with thread-safe operations."""

    def __init__(self) -> None:
        """
        Input: None
        Output: None
        Purpose: Initialize the client mapper
        Description: Creates an empty map and initializes thread lock for synchronization
        """
        self.__map: Dict[str, str] = {}
        self.__lock = Lock()

    def add_client(self, ip: str, domain: str) -> None:
        """
        Input: ip (str) - Client IP address, domain (str) - Domain requested by client
        Output: None
        Purpose: Add or update client mapping
        Description: Maps a client IP to their requested domain in a thread-safe manner
        """
        self.get_map()
        with self.__lock:
            self.__map[ip] = domain
        self.save_map()

    def get_domain(self, ip: str) -> str:
        """
        Input: ip (str) - Client IP address to look up
        Output: str - Domain associated with the IP
        Purpose: Retrieve and remove domain mapping for an IP
        Description: Gets and removes the domain mapping for a client IP, returning default if not found
        """
        self.get_map()
        if ip == "127.0.0.1":
            ip = SERVER_IP
        with self.__lock:
            to_return = self.__map.pop(ip, "www.default.com")
        self.save_map()
        return to_return

    def get_map(self) -> None:
        """
        Input: None
        Output: None
        Purpose: Load client mappings from file
        Description: Attempts to load the IP-domain mappings from map.json, creates empty map if file not found
        """
        with self.__lock:
            try:
                with open('map.json', 'r') as f:
                    self.__map = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.__map = {}

    def save_map(self) -> None:
        """
        Input: None
        Output: None
        Purpose: Save client mappings to file
        Description: Saves the current IP-domain mappings to map.json in a thread-safe manner
        """
        with self.__lock:
            with open('map.json', 'w') as f:
                json.dump(self.__map, f)
