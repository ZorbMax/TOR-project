import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((socket.gethostname(), 55555))
clients = []
publicKeys = []

while True:
    data, address = sock.recvfrom(128)
    if data.decode().strip() == 'client':
        print('connection from a client: {}'.format(address))
        for client in clients:
            addr, port = client
            sock.sendto('{} {}'.format(addr, port).encode(), address)
        sock.sendto(b'end', address)
    else:
        print('connection from: {}'.format(address))
        sock.sendto(b'ready', address)

        for client in clients:
            addr, port = address
            addr2, port2 = client
            sock.sendto('{} {}'.format(addr, port).encode(), client)
            sock.sendto('{} {}'.format(addr2, port2).encode(), address)

        sock.sendto(b'end', address)
        clients.append(address)