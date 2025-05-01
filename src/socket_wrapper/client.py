from socket_wrapper.network_wrapper import NetworkWrapper

class Client(NetworkWrapper):
    def __init__(self, ip: str, port: int) -> None:
        super().__init__()
        self.__ip = ip
        self.__port = port

        self._serv_sock.connect((self.__ip, self.__port))
    
    
    def recv_by_size(self) -> bytes: #type:ignore
        return super().recv_by_size(self._serv_sock)
    
    def send_by_size(self, to_send: bytes): #type:ignore
        return super().send_by_size(to_send, self._serv_sock)
    
    def parse(self, from_server: bytes) -> tuple[str,str]:
        """Parse server response

        Args:
            from_server (bytes): message from server

        Raises:
            Exception: if unknown message type

        Returns:
            string: message to show user.
            string: message type  - error, success
        """
        fields = from_server.split(b'~')
        code = fields[0]
        
        if code == b'':
            return "",""
        elif code == b'ACK':
            return "Action was done successfully","success"
        elif code == b'STATS':
            return "NOT IMPLEMENTED","" #TODO 
        elif code == b'URL':
            return f"Url - {fields[1].decode()}","success"
        elif code == b'ERR':
            return f"Action failed - {fields[2].decode()}","error"
        else:
            raise Exception("Unknown code")
    
    

    def client_hello(self) -> bytes:
        return b'HELLO'

    
    
    def cleanup(self):
        self._serv_sock.close()
    
    def sign_up(self, username: str, password: str, cpassword: str, err: str = "") -> bytes:
        # Return formatted request for sign-up
        return f"SIGN_UP~{username}~{password}~{cpassword}".encode()

    def login(self, username: str, password: str, err: str = "") -> bytes:
        # Return formatted request for login
        return f"SIGN_IN~{username}~{password}".encode()

    def add_url(self, url: str, err: str = "") -> bytes:
        # Return formatted request to add a URL
        return f"ADD~{url}".encode()

    def remove_url(self, fake_url: str, err: str = "") -> bytes:
        # Return formatted request to remove a URL
        return f"DEL~{fake_url}".encode()

    def get_real_url(self, fake_url: str, err: str = "") -> bytes:
        # Return formatted request to get the real URL
        return f"GET~{fake_url}".encode()

    def req_info(self, fake_url: str, err: str = "") -> bytes:
        # Return formatted request to fetch request info
        return f"REQ~{fake_url}".encode()
