
import traceback

from socket_wrapper import Client





def main():
    ip,port = "127.0.0.1",12344
    client: Client = Client(ip,port)
    try :
        username = input("Username: ")
        password = input("Password: ")
        client.send_by_size(client.client_hello(username,password))
        server_hello = client.recv_by_size() #TODO logic.
        while True:
            to_send = client.start_gui()
            client.send_by_size(to_send)
            from_server = client.recv_by_size()
            to_send = client.parse(from_server)

    except Exception as err:
        print(f'General error: {err}')
        print(traceback.format_exc())
    finally:
        client.cleanup()


        
    print ('Bye')


if __name__ == "__main__":
    main()