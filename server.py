import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((socket.gethostname(), 60000))

while True:
    data= sock.recv(4048).decode()
    print(data)