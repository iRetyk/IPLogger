
import subprocess
import time
import traceback
import os
from pathlib import Path

from socket_wrapper import Server


process_list: list[subprocess.Popen]



            

def start_processes(host_ip: str,target_ip: str,router_ip: str) -> None:
    """
    ths function will start all the proceses that run in the background.
    
    http server
    dns poisonig
    arp spoofing (not implemnted)
    """
    global process_list
    http_process = subprocess.Popen(["/home/pablo/idan/dev/project/.venv/bin/python3","src/http_helper.py"])
    dns_process = subprocess.Popen(["/home/pablo/idan/dev/project/.venv/bin/python3","src/dns_poison.py"])
    #arp_process = subprocess.Popen(["python","arp_spoofer.py"])
    process_list = [http_process,dns_process]


def kill_processes() -> None:
    """
    stop spoofing, by killing spoofer process.
    """
    print("Killing processes....")
    for p in process_list:
        try:
            p.terminate()
            time.sleep(0.1)
            print("Process killed")
        except Exception as e:
            print("couldn't kill process" + str(p))
            print(str(e))


def main():


    
    host_ip, target_ip,router_ip = "192.168.1.128","192.168.1.143","192.168.1.1"
    start_processes(host_ip, target_ip,router_ip)
    

    try:
        print("Binded server, waiting......")
        server: Server = Server(12344)
        
        
        while True:
            
            from_client: bytes  = server.recv_by_size()
            if not from_client:
                break
            to_send = server.parse(from_client)
            
            server.send_by_size(to_send)
        
        
    except Exception as err:
        print(f'General error: {err}')
        print(traceback.format_exc())
    finally:
        try:
            server.cleanup() #type:ignore
        except:
            pass
        kill_processes()


if __name__ == "__main__":
    main()