import hashlib
import random
import socket
import string
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

password = str(input('Enter the correct password for the user here : '))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((socket.gethostname(), 60000))
def random_token_generator(size=16, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

while True:
    data, address = sock.recvfrom(4048)
    data = data.decode()
    if data == "connect request":
        testToken = random_token_generator().encode()
        sock.sendto(testToken, address)
        key = hashlib.md5()
        key.update(password.encode())
        iv = b'This is an IV456'
        cipher = Cipher(algorithms.AES(key.hexdigest().encode()), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ct = encryptor.update(testToken) + encryptor.finalize()
        data = sock.recv(4048).decode()
        if str(ct) == str(data):
            print("Authentication succeeded")
            sock.sendto(b"Success", address)
        else:
            print("Password false")
            sock.sendto(b"Fail", address)