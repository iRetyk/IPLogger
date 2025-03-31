import socket
import random
import string
import json



class Server:
    
    func_table: dict[bytes,str] = {
        b'code':"corresponding function",
        b'ADD': "add_url"
    }
    
    urls_path = "../urls.json"
    
    def __init__(self,port: int) -> None:
        self.__ip = "127.0.0.1" # Host ip
        self.__port = port
        
        self.__sock = socket.socket()
        
        self.__sock.bind((self.__ip,self.__port))
        self.__sock.listen(100)
    
    
    def recv_by_size(self) -> bytes:
        """Recv message from client, using size field to ensure getting all the message.

        Returns:
            bytes: the message from client without size fields. 
            b'': if the client disconnect, or other error occurred.
        """
        msg_size: bytes = b'' 
        while not b'~' in msg_size:
            msg_size += self.__sock.recv(4)
            if (not msg_size): # msg_size is empty - Client disconnected
                return b'' # Return empty string to indicate the issue
        
        size_in_bytes,msg  = msg_size.split(b'~',1)
        size = int(size_in_bytes.decode())
        
        while(len(msg) != size):
            msg += self.__sock.recv(128)
        
        
        return msg
    
    def parse(self, data: bytes) -> bytes:
        """Parse data, call apropriate function in Server class.
        Performs the actions required, and return answer according to protocol

        Args:
            data (bytes): data from server

        Returns:
            bytes: answer according to protocol
        """
        fields: list[bytes] = data.split(b'~')
        
        code: bytes = fields[0]
        
        result: bytes = eval(f"self.{Server.func_table[code]}(*fields[1:])")
        return result
    
    def server_hello(self):
        pass
    
    def show_stats(self):
        pass
    
    def add_url(self,real_url: bytes):
        """
        Message Format:
        ADD~<real_url>
        """
        with open(Server.urls_path, "r") as f:
            try:
                urls: dict[str, str] = json.load(f)
            except json.JSONDecodeError:
                urls = {}  # Handle an empty or malformed JSON file
        
        urls[self.generate_fake_url()] = real_url.decode()
        
        with open(Server.urls_path, "w") as f:
            json.dump(urls,f,indent=4)
        pass
    
    def get_url(self):
        pass
    
    def remove_url(self):
        pass
    
    
    
    ###### Helper functions - shouldn't be called by instance of the class #########
    
    
    def generate_fake_url(self) -> str:
        """Generate a slightly realistic fake URL with a domain and path."""
        tlds = ['com', 'net', 'org', 'info', 'biz']
        words = ["tech", "cloud", "data", "hub", "media", "net", "shop", "world", "global", "secure"]
        
        random_string = lambda length: ''.join(random.choices(string.ascii_lowercase, k=length))
        
        domain = f"{random.choice(words)}{random_string(3)}.{random.choice(tlds)}"
        path = f"/{random.choice(words)}{random_string(2)}/{random_string(4)}"
        
        return f"https://{domain}{path}"


