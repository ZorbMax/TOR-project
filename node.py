import socket
import threading

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding



def newNode(myport):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    listOfNodes = []
    rendezvous = (socket.gethostbyname(socket.gethostname()), 55555)

    # connect to rendezvous
    print('connecting to rendezvous server')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((socket.gethostname(), myport))
    sock.sendto('StoreKey {}'.format(pem.decode()).encode(), rendezvous)

    while True:
        data = sock.recv(4092).decode()

        if data.strip() == 'ready':
            print('checked in with server, waiting')
            break

    data = sock.recv(4092).decode()
    while data.strip() != 'end':
        ip, dport, key = data.split(' ', 2)
        dport = int(dport)
        listOfNodes.append(((ip, dport), key))
        data = sock.recv(4092).decode()

    def decrypt(encrypted):
        original_message = private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return original_message.decode()

    def connected(previousNode):
        connected = True
        while connected:
            data, adress = sock.recvfrom(4092)
            if(len(data.decode().split("#####", 1)) > 1):
                key, data = data.decode().split("#####", 1)
                key = decrypt(eval(key))
                f = Fernet(key)
                data = f.decrypt(eval(data)).decode()
                nextHop, data = data.split("#####", 1)
                mylist = []
                for i in nextHop.split("/"):
                    mylist.append(i)
                nextHop = (mylist[0], int(mylist[1]))
                sock.sendto(data.encode(), nextHop)
            else:
                sock.sendto(data, previousNode)
                if data.strip() == "stop":
                    connected = False

    while True:
        data, adress = sock.recvfrom(4092)
        if '{}'.format(adress) == str(rendezvous):
            ip, port, key = data.decode().split(' ', 2)
            port = int(port)
            listOfNodes.append(((ip, port),key))
        else:
            key, data = data.decode().split("#####", 1)
            key = decrypt(eval(key))
            f = Fernet(key)
            data = f.decrypt(eval(data)).decode()
            nextHop, data = data.split("#####", 1)
            mylist = []
            for i in nextHop.split("/"):
                mylist.append(i)
            nextHop = (mylist[0], int(mylist[1]))
            sock.sendto(data.encode(), nextHop)
            connected(adress)