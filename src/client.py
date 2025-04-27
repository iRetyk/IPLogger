import sys
import traceback

from socket_wrapper import Client



def main():
    ip,port = "127.0.0.1",12344
    client: Client = Client(ip,port)
    try :
        client.send_by_size(client.start_menu())
        from_server: bytes = client.recv_by_size()
        to_send = client.parse(from_server) # Handle errors.
        if to_send == b'':
            sys.exit()
        # Reaching this point will happen only when the first stage completed - received ack from server.
        if from_server == b'ACK':
            print("Action was successful")
        while True:
            to_send = client.main_menu()
            client.send_by_size(to_send)
            from_server = client.recv_by_size()
            to_send = client.parse(from_server)
            if to_send == b'':
                break

    except Exception as err:
        print(f'General error: {err}')
        print(traceback.format_exc())
    finally:
        client.cleanup()


        
    print ('Bye')


if __name__ == "__main__":
    main()