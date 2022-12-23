import socket
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

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((socket.gethostname(), myport))
    sock.sendto('StoreKey {}'.format(pem.decode()).encode(), rendezvous)

    while True:
        data = sock.recv(4092).decode()
        if data.strip() == 'ready':
            break

    data = sock.recv(4092).decode()
    while data.strip() != 'end':
        ip, dport, key = data.split(' ', 2)
        dport = int(dport)
        listOfNodes.append(((ip, dport), key))
        data = sock.recv(4092).decode()

    """
    Function used to decrypt data using the private key of this node
    """
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

    """
    Main thread handling data received by the node
    """
    while True:
        data, address = sock.recvfrom(4092)
        if '{}'.format(address) == str(rendezvous):
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

            data = sock.recv(4092)
            sock.sendto(data, address)