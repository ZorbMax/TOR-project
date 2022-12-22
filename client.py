import socket
import random

"""
TO DO : update listOfNodes when a new node is added in the network
"""

listOfNodes = []
rendezvous = (socket.gethostname(), 55555)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((socket.gethostname(), 49999))
sock.sendto(b'client', rendezvous)

data = sock.recv(1024).decode()
while data.strip() != 'end':
    print(data)
    ip, dport = data.split(' ')
    dport = int(dport)
    listOfNodes.append((ip, dport))
    data = sock.recv(1024).decode()


"""
TO DO : temp list keeping track of nodes already used
"""
gatewayNode = listOfNodes[random.randint(0, len(listOfNodes)-1)]
middleRelay = listOfNodes[random.randint(0, len(listOfNodes)-1)]

while middleRelay == gatewayNode:
    middleRelay = listOfNodes[random.randint(0, len(listOfNodes)-1)]

exitRelay = listOfNodes[random.randint(0, len(listOfNodes)-1)]
while exitRelay == gatewayNode or exitRelay == gatewayNode:
    exitRelay = listOfNodes[random.randint(0, len(listOfNodes)-1)]

strMiddleRelay = ""
strExitRelay = ""
for i in middleRelay:
    strMiddleRelay += str(i) + "/"
for i in exitRelay:
    strExitRelay += str(i) + "/"

msg = "Bonjour Bob"
encrypted = strMiddleRelay + "#" + strExitRelay + "#" + msg
sock.sendto('{}'.format(encrypted).encode(), gatewayNode)