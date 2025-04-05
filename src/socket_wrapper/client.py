import sys
import os

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))
from socket_wrapper.network_wrapper import NetworkWrapper
#from ...ui import app

class Client(NetworkWrapper):
    def __init__(self, ip: str, port: int) -> None:
        super().__init__()
        self.__ip = ip
        self.__port = port

        self._sock.connect((self.__ip, self.__port))
    
    def parse(self,from_server: bytes):
        fields = from_server.split(b'~')
        code = fields[0]
        if code == b'ACK':
            pass # Nothing needs to happen
        elif code == b'STATS':
            self.display_stats(fields[1:])
        elif code == b'URL':
            self.display_url(fields[1])
        elif code == b'ERR':
            # If received error, handle error will simply ask the user again for the input that got an error. 
            # Than parse it again.  
            server_response = self.handle_error(fields[1:])
            return self.parse(server_response)
        else:
            raise Exception("Unknown code")
    
    

    def client_hello(self,username,password) -> bytes:
        return f'HELLO~{username}~{password}'.encode()

    def start_gui(self) -> bytes:
        print("\n###################")
        print("What do you want to do?")
        print(" 1 - add url")
        print(" 2 - remove url")
        print(" 3 - get url")
        print(" 4 - req info")
        print(" 9 - exit")
        print("\n---------------------")
        choice: str = input(" >>> ")
        if choice == "9":
            return b''
        funciton_list = [self.add_url,self.remove_url,self.get_real_url,self.req_info]
        to_send = funciton_list[int(choice) - 1]()
        return to_send
    
    def handle_error(self, fields: list[bytes]) -> bytes:
        """
        If received error, this function will be called. 
        According to error code, call appropriate function, and repeat user input (GUI)
        This logic happens until an ERROR is no longer received.
        """
        function_number, error_code = fields
        match int(function_number): 
            case 0: # add_url
                pass
            
            case 1: # remove_url
                
                match int(error_code):
                    case 0: # url not found
                        self.remove_url()
            
            case 2: # get_real_url
                
                match int(error_code):
                    case 0: # url not found
                        self.get_real_url()
            
        return self.recv_by_size()
        
        """
            func_table: dict[bytes,Callable] = {
        b"ADD": add_url,
        b"DEL": remove_url,
        b"GET": get_real_url,
        b"HELLO": server_hello
    }
        """
    
    
    def cleanup(self):
        self._sock.close()
    
    def display_url(self, url):
        """
        Show user the url.
        """
        print(url)

    def display_stats(self,*args):
        raise NotImplementedError
    def add_url(self, err: str = "") -> bytes:
        # Input from user the url.
        # Then build and return the request.
        print("Enter url: ")
        fake_url = input(" >")
        return f'ADD~{fake_url}'.encode()

    def remove_url(self, err: str = "") -> bytes:
        # Input from user the url.
        # Build and return the request.
        print("Enter url: ")
        fake_url = input(" >")
        return f'DEL~{fake_url}'.encode()


    def get_real_url(self, err: str = "") -> bytes:
        # Input from user the url.
        # Build and return the request.
        print("Enter url: ")
        fake_url = input(" >")
        return f'GET~{fake_url}'.encode()


    def req_info(self, err: str = "") -> bytes:
        # Input from user the url.
        # Then build and return the request.
        print("Enter url: ")
        fake_url = input(" >")
        return f'REQ~{fake_url}'.encode()