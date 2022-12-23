import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((socket.gethostname(), 60000))

while True:
    data, address = sock.recvfrom(4048)
    data = data.decode()
    print(data)
    sock.sendto("Bien reçu : {}".format(data).encode(), address)