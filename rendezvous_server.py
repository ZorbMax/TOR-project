import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((socket.gethostname(), 55555))
clients = []
addrClient = 0

while True:
    data, address = sock.recvfrom(128)
    data = data.decode()
    addr, port = address
    if data.strip() == 'client':
        addrClient = address
        print('connection from a client: {}'.format(address))
        for client in clients:
            addr, port = client[0]
            sock.sendto('{} {} {}'.format(addr, port, client[1]).encode(), address)
        sock.sendto(b'end', address)
    elif data.split()[0] == 'StoreKey':
        print('connection from: {}'.format(address))
        sock.sendto(b'ready', address)
        key = data[data.find(" "):]
        for client in clients:
            addr2, port2 = client[0]
            sock.sendto('{} {} {}'.format(addr, port, key).encode(), client[0])
            sock.sendto('{} {} {}'.format(addr2, port2, client[1]).encode(), address)
        if addrClient != 0:
            sock.sendto('update {} {} {}'.format(addr, port, key).encode(), addrClient)
        sock.sendto(b'end', address)
        clients.append((address,key))
    else:
        print('error')