import socket
import threading
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


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
    sock.sendto('StoreKey {}'.format(pem).encode(), rendezvous)

    while True:
        data = sock.recv(1024).decode()

        if data.strip() == 'ready':
            print('checked in with server, waiting')
            break

    data = sock.recv(1024).decode()
    while data.strip() != 'end':
        ip, dport, key = data.split(' ', 2)
        dport = int(dport)
        listOfNodes.append(((ip, dport), key))
        data = sock.recv(1024).decode()

    # listen for
    # equiv: nc -u -l 50001
    def listen():
        while True:
            data, adress = sock.recvfrom(1024)
            data = data.decode()
            if '{}'.format(adress) == str(rendezvous):
                ip, port, key = data.split(' ',2)
                port = int(port)
                listOfNodes.append(((ip, port),key))
            else:
                list = data.split('#')
                if len(list) > 1:
                    mylist = []
                    for i in list[0].split("/"):
                        mylist.append(i)
                    nextHop = (mylist[0], int(mylist[1]))
                    data = '#'.join(list[1:len(list)])
                    print(str(myport) + " reçu : " + data)
                    sock.sendto('{}'.format(data).encode(), nextHop)
                else:
                    print(list[0])


    listener = threading.Thread(target=listen, daemon=True);
    listener.start()

    # send messages
    # equiv: echo 'xxx' | nc -u -p 50002 x.x.x.x 50001

    while True:
        x = 1
        #sock.sendto(msg.encode(), (ip, dport))