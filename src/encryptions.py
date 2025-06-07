import random
from socket import socket
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA


PUBLIC_KEY,PRIVATE_KEY = bytes(),bytes()


def AES_encrypt(key:bytes, data: bytes):
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    ciphertext = cipher.encrypt(pad(data, AES.block_size))
    return iv, ciphertext

def AES_decrypt(key : bytes, iv, data):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(data), AES.block_size)

# Server Method
def generate_keys_RSA():
    """
    generates keys for RSA
    
    returns:
    tuple(private_key, public_key)
    """
    
    
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

# Server Method
def AES_key_exchange_server(sock:socket) -> bytes:
    """
    swaps with client keys for AES using RSA
    first the server sends public key, than client sends AES key encrypted using the public key, than server decrypts the AES key. Handshake done
    

    Args:
        sock (socket): the socket

    Returns:
        bytes: AES key
    """
    
    sock.send(PUBLIC_KEY)
    


    
    enc_key = sock.recv(1024)

    AES_key = PKCS1_OAEP.new(RSA.import_key(PRIVATE_KEY)).decrypt(enc_key)
    
    print("Received key:", AES_key)
    return AES_key


def RSA_decrypt(private, enc_key):
    AES_key = PKCS1_OAEP.new(RSA.import_key(private)).decrypt(enc_key)
    return AES_key

# Client methods

def AES_key_exchange_client(sock: socket) -> bytes:
    """
    swaps with server keys for AES using RSA
    first the server sends public key, than clinet sends AES key encrypted using the public key, than server decrypts the AES key. Handshake done
    

    Args:
        sock (socket): the socket

    Returns:
        bytes: AES key
    """

    aes_key = generate_AES_key()

    server_key = sock.recv(1024)
    sock.send(PKCS1_OAEP.new(RSA.import_key(server_key)).encrypt(aes_key))
    print("Sent key: ", aes_key)
    return aes_key


def generate_AES_key() -> bytes:
    #generate AES key randomly and return it
    return bytes(random.randint(0,255) for _ in range(16))

def RSA_encrypt(server_key, aes_key):
    return PKCS1_OAEP.new(RSA.import_key(server_key)).encrypt(aes_key)