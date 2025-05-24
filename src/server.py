import subprocess
import time
import traceback

from pathlib import Path
from typing import List, Optional
from socket_wrapper import Server

process_list: List[subprocess.Popen] = []

def start_processes(host_ip: str, target_ip: str, router_ip: str) -> None:
    """
    Input: host_ip (str) - Host IP address, target_ip (str) - Target IP address,
           router_ip (str) - Router IP address
    Output: None
    Purpose: Start background processes for network operations
    Description: Launches HTTP server and DNS poisoning processes, maintaining their references
                in a global list
    """
    global process_list

    http_process = subprocess.Popen(["python", "src/http_helper.py"])
    dns_process = subprocess.Popen(["python", "src/dns_poison.py"])
    #arp_process = subprocess.Popen(["python","arp_spoofer.py"])
    process_list = [http_process, dns_process]

def kill_processes() -> None:
    """
    Input: None
    Output: None
    Purpose: Stop all background processes
    Description: Terminates all running background processes gracefully with error handling
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

def main() -> None:
    """
    Input: None
    Output: None
    Purpose: Main server execution function
    Description: Initializes and runs the server, handling client connections and cleanup operations
    """
    host_ip, kid_ip, router_ip = "127.0.0.1", "127.0.0.1", "127.0.0.1"
    start_processes(host_ip, kid_ip, router_ip)
    server: Optional[Server] = None
    try:
        print("Binded server, waiting......")
        server = Server(host_ip,12344) # IP,Port

        while True:
            from_client: bytes = server.recv_by_size()
            if not from_client:
                break
            to_send = server.parse(from_client)
            server.send_by_size(to_send)

    except Exception as err:
        print(f'General error: {err}')
        print(traceback.format_exc())
    finally:
        try:
            if server is not None:
                server.cleanup()
        except:
            pass
        kill_processes()

if __name__ == "__main__":
    main()
