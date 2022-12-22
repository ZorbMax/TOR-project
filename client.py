import socket
import random
import threading

"""
TO DO : update listOfNodes when a new node is added in the network : DONE
"""
listOfNodes = []
rendezvous = (socket.gethostname(), 55555)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((socket.gethostname(), 49999))
sock.sendto(b'client', rendezvous)

data = sock.recv(1024).decode()
while data.strip() != 'end':
    print(data)
    ip, port, public_key = data.split(' ',2)
    port = int(port)
    listOfNodes.append(((ip, port), public_key))
    data = sock.recv(1024).decode()

def listen():
    while True:
        data = sock.recv(1024).decode()
        print(data)
        if data.split(' ')[0] == 'update':
            command, ip, newPort, public_key = data.split(' ',3)
            listOfNodes.append(((ip, int(newPort)), public_key))
listener = threading.Thread(target=listen, daemon=True)
listener.start()


"""
TO DO : temp list keeping track of nodes already used : DONE
"""
def randomNode():
    r = list(range (0, len(listOfNodes)))
    gatewayNode = listOfNodes[r.pop(random.randint(0, len(r)-1))][0]
    middleRelay = listOfNodes[r.pop(random.randint(0, len(r)-1))][0]
    exitRelay = listOfNodes[r.pop(random.randint(0, len(r)-1))][0]
    strMiddleRelay = '/'.join(map(str, middleRelay))
    strExitRelay = '/'.join(map(str, exitRelay))
    return gatewayNode, strMiddleRelay, strExitRelay
def goMsg():
    while True:
        msg = str(input('Enter your message here : '))
        gatewayNode, strMiddleRelay, strExitRelay = randomNode()
        print(gatewayNode)
        encrypted = strMiddleRelay + "#" + strExitRelay + "#" + msg
        sock.sendto('{}'.format(encrypted).encode(), gatewayNode)
listener = threading.Thread(target=goMsg, daemon=True)
listener.start()
while True:
    x = 1