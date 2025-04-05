
import traceback

from socket_wrapper import Client





def main():
    ip,port = "",12345
    client: Client = Client(ip,port)
    try :
        username = input("Username: ")
        password = input("Password: ")
        client.client_hello(username,password)
        
        while True:
            to_send = client.start_gui()
            client.send_by_size(to_send)
            from_server = client.recv_by_size()
            client.parse(from_server)

    except Exception as err:
        print(f'General error: {err}')
        print(traceback.format_exc())


        
    print ('Bye')
