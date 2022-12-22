import socket
import random
import threading
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

"""
TO DO : update listOfNodes when a new node is added in the network : DONE
"""
listOfNodes = []
rendezvous = (socket.gethostname(), 55555)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((socket.gethostname(), 49999))
sock.sendto(b'client', rendezvous)

data = sock.recv(4092).decode()
while data.strip() != 'end':
    ip, port, public_key = data.split(' ',2)
    port = int(port)
    listOfNodes.append(((ip, port), public_key))
    data = sock.recv(4092).decode()

def listen():
    while True:
        data = sock.recv(4092).decode()
        if data.split(' ')[0] == 'update':
            command, ip, newPort, public_key = data.split(' ',3)
            listOfNodes.append(((ip, int(newPort)), public_key))
listener = threading.Thread(target=listen, daemon=True)
listener.start()


"""
TO DO : temp list keeping track of nodes already used : DONE
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
def randomNode():
    r = list(range (0, len(listOfNodes)))
    gatewayNode = listOfNodes[r.pop(random.randint(0, len(r)-1))]
    middleRelay = listOfNodes[r.pop(random.randint(0, len(r)-1))]
    exitRelay = listOfNodes[r.pop(random.randint(0, len(r)-1))]
    strMiddleRelay = '/'.join(map(str, middleRelay))
    strExitRelay = '/'.join(map(str, exitRelay))
    return gatewayNode, middleRelay, exitRelay, strMiddleRelay, strExitRelay
def goMsg():
    while True:
        msg = str(input('Enter your message here : '))
        gatewayNode, middleRelay, exitRelay, strMiddleRelay, strExitRelay = randomNode()
        #encrypted = encrypt(strMiddleRelay[0] + "#" + encrypt(strExitRelay[0] + "#" + encrypt(msg, exitRelay[1].encode()), middleRelay[1].encode()),gatewayNode[1].encode())
        encrypted = encrypt(msg.encode(), gatewayNode[1].encode())
        sock.sendto(encrypted, gatewayNode[0])
listener = threading.Thread(target=goMsg, daemon=True)
listener.start()
while True:
    x = 1