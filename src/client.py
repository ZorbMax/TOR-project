import hashlib
import socket
import random
import threading

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


listOfNodes = []
rendezvous = (socket.gethostname(), 55555)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((socket.gethostname(), 49999))

sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2.bind((socket.gethostname(), 49998))

sock2.sendto(b'client', rendezvous)
data = sock2.recv(4092).decode()
while data.strip() != 'end':
    ip, port, public_key = data.split(' ', 2)
    port = int(port)
    listOfNodes.append(((ip, port), public_key))
    data = sock2.recv(4092).decode()


"""
Thread used by the client to update the list of nodes if a new node is added to the network (directory_server will send the informations)
"""
def listen():
    while True:
        data = sock2.recv(4092).decode()
        if data.split(' ')[0] == 'update':
            command, ip, newPort, public_key = data.split(' ',3)
            listOfNodes.append(((ip, int(newPort)), public_key))
listener = threading.Thread(target=listen, daemon=True)
listener.start()


"""
Used to encrypt data using a given Public key (pem)
"""
def encrypt(msg, pem):
    public_key = serialization.load_pem_public_key(
        pem,
        backend = default_backend()
    )
    encrypted = public_key.encrypt(
        msg,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted

"""
Generate a routing that the data send by the client will use and get the public keys of the nodes in the routing
"""
def randomNode():
    r = list(range (0, len(listOfNodes)))
    gatewayNode = listOfNodes[r.pop(random.randint(0, len(r)-1))]
    middleRelay = listOfNodes[r.pop(random.randint(0, len(r)-1))]
    exitRelay = listOfNodes[r.pop(random.randint(0, len(r)-1))]
    strMiddleRelay = '/'.join(map(str, middleRelay[0]))
    strExitRelay = '/'.join(map(str, exitRelay[0]))
    return gatewayNode, middleRelay, exitRelay, strMiddleRelay, strExitRelay


"""
Add a layer of encryption on the data and informations about the next node in the network
"""
def addHop(data, address, key, fernet):
    messagePackage = (address, data)
    messagePackage = '#####'.join(map(str, messagePackage))
    enc_data = fernet.encrypt(messagePackage.encode())
    enc_data = (key, enc_data)
    enc_data = '#####'.join(map(str, enc_data))
    enc_data = str(enc_data)
    return enc_data

"""
Generate 3 symmetric keys for the layers of encryption and use them to create the data that will go through our network
"""
def tripleEncryption(data, publickey1, publickey2, publickey3, address1, address2, address3):
    symmetricKey1, symmetricKey2, symmetricKey3 = Fernet.generate_key(), Fernet.generate_key(), Fernet.generate_key()
    f, f2, f3 = Fernet(symmetricKey1), Fernet(symmetricKey2), Fernet(symmetricKey3)
    encryptedKey1, encryptedKey2, encryptedKey3 = encrypt(symmetricKey1, publickey1), encrypt(symmetricKey2, publickey2), encrypt(symmetricKey3, publickey3)
    result = addHop(addHop(addHop(data, address3, encryptedKey3, f3), address2, encryptedKey2, f2), address1, encryptedKey1, f)
    return result.encode()

while True:
    gatewayNode, middleRelay, exitRelay, strMiddleRelay, strExitRelay = randomNode()
    password = str(input('Enter your password here : '))
    strDestination = '/'.join(map(str, (socket.gethostbyname(socket.gethostname()), 60000)))
    data = tripleEncryption("connect request", gatewayNode[1].encode(), middleRelay[1].encode(), exitRelay[1].encode(),
                            strMiddleRelay, strExitRelay, strDestination)
    sock.sendto(data, gatewayNode[0])
    testToken = sock.recv(1024)
    key = hashlib.md5()
    key.update(password.encode())
    iv = b'This is an IV456'
    cipher = Cipher(algorithms.AES(key.hexdigest().encode()), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ct = encryptor.update(testToken) + encryptor.finalize()
    data = tripleEncryption(ct, gatewayNode[1].encode(), middleRelay[1].encode(), exitRelay[1].encode(),
                            strMiddleRelay, strExitRelay, strDestination)
    sock.sendto(data, gatewayNode[0])
    data = sock.recv(1024).decode()
    if data == "Success":
        print("Connected to server")
    else:
        print("Wrong password")