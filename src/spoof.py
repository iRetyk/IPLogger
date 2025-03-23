"""
this file's purpose is:
the server should activate this script in a distinct process, 
and than kills it, when shutting down.
"""


DEBUG = True


import sys
import signal
import time
import random

from netwroking import Spoofer

if (len(sys.argv) != 4):
    print("Wrong usage. Usage- spoof.py <host_ip> <target_ip> <router_ip>")
    sys.exit(0)


class Spoof():
    def __init__(self) -> None:
        self.__spoof_obj : Spoofer = Spoofer(*sys.argv)
        # Setup signal handler function as the signal function.
        signal.signal(signal.SIGTERM,self.signal_handler)

    def signal_handler(self,sig,frame):
        print("Shutting down....")
        self.__spoof_obj.checkout()
        sys.exit(0)


    def spoof(self):
        while True:
            self.__spoof_obj.spoof()
            time.sleep(random.random()/5) # wait a random number between 0-0.2
            # The time.sleep has 2 jobs - 
            #   first, make the spoof harder to notice.
            #   second, the signal can only be received if the process is waiting, and not running.
            #       thus, without the time the signal wouldn't be registered.


def debug_main():
    while True:
        print("Sent packet.... (not really)")
        time.sleep(1)


def main():
    spoofer = Spoof()
    spoofer.spoof()

if __name__ == "__main__":
    if DEBUG:
        debug_main()
    else:
        main()

