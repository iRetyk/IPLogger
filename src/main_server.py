import subprocess
import time
import traceback
import threading
import time

from socket import socket, timeout as socket_timeout
from pathlib import Path
from typing import List, Optional, Set, Dict
from socket_wrapper import Server



process_list = []

class ServerManager:
    """Manager class for handling multiple client connections."""

    def __init__(self, host_ip: str, port: int):
        """
        Input: host_ip (str) - Host IP address, port (int) - Port number
        Output: None
        Purpose: Initialize server manager
        Description: Creates server instance and initializes client tracking
        """
        self.server = Server(host_ip, port)  # Single server instance
        self.client_sockets: Set[socket] = set()
        self.running = True
        
        

    
    def run(self) -> None:
        """
        Input: None
        Output: None
        Purpose: Start accepting client connections
        Description: Continuously accepts new clients and creates handler threads
        """
        while self.running:
            try:
                client_socket, _ = self.server._serv_sock.accept()
                client_socket.settimeout(1.0)  # Set timeout on client socket
                self.client_sockets.add(client_socket)
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket,)
                )
                thread.daemon = True  # Background thread that will exit when main thread exits
                thread.start()
            except socket_timeout:
                continue  # Keep trying if no clients are connecting
            except Exception as e:
                if not self.running:  # If we're shutting down
                    break
                print(f"Error accepting client connection: {e}")

    def handle_hello(self,client_socket) -> bytes:
        return self.server.exchange_keys(client_socket)
    
    
    def handle_client(self, client_socket: socket) -> None:
        """
        Input: client_socket (socket) - Socket for the client connection
        Output: None
        Purpose: Handle communication with a specific client
        Description: Continuously receives and processes messages from the client
        """
        client_address = client_socket.getpeername()
        print(f"New client connected from {client_address}")
        try:
            client_AES_key = self.handle_hello(client_socket)
            while self.running:
                data = self.server.recv_by_size(client_AES_key,client_socket)
                if not data:  # Empty data means timeout or disconnection
                    if self.running:  # If we're not shutting down, keep listening
                        continue
                    break
                try:
                    response = self.server.parse(data)
                    self.server.send_by_size(response,client_AES_key, client_socket)
                except socket_timeout:
                    continue  # Try again on timeout
                except Exception:
                    break  # Break on other errors (like disconnection)
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            self.client_sockets.remove(client_socket)
            client_socket.close()
            print(f"Client disconnected from {client_address}")

    def cleanup(self) -> None:
        """
        Input: None
        Output: None
        Purpose: Clean up server manager resources
        Description: Stops the server and closes all client connections
        """
        self.running = False
        for sock in self.client_sockets:
            sock.close()
        self.server.cleanup()

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

    arp_process = subprocess.Popen(["python","src/arp_spoofer.py",host_ip,target_ip,router_ip])
    dns_process = subprocess.Popen(["python", "src/dns_poison.py"])
    time.sleep(2)
    http_process = subprocess.Popen(["python", "src/http_helper.py"])
    process_list = [arp_process, dns_process,http_process]

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
    Description: Initializes and runs the server manager, handling client connections and cleanup
    """
    host_ip, kid_ip, router_ip = "127.0.0.1", "127.0.0.1", "127.0.0.1"
    start_processes(host_ip, kid_ip, router_ip)
    server_manager: Optional[ServerManager] = None

    try:
        print("Starting server, waiting for connections...")
        server_manager = ServerManager(host_ip, 12343)
        server_manager.run()  # This will run until interrupted
    except Exception as err:
        print(f'General error: {err}')
        print(traceback.format_exc())
    finally:
        try:
            if server_manager is not None:
                server_manager.cleanup()
        except:
            pass
        kill_processes()

if __name__ == "__main__":
    main()
