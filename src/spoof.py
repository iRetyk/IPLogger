import sys
import signal
from netwroking import Spoofer

if (len(sys.argv) != 3):
    print("Wrong usage. Usage- spoof.py <host_ip> <target_ip> <router_ip>")
    sys.exit(0)


host_ip,target_ip,router_ip = sys.argv




spoof_obj : Spoofer = Spoofer(*sys.argv)
spoof_obj.spoof()



def signal_handler(sig,frame):
    print("Shutting down....")
    spoof_obj.checkout()
    sys.exit(0)
signal.signal(signal.SIGTERM,signal_handler)