import socket
from random import randint

server_name = "200010048_server"
port_number = 80
host_ip = "localhost"

random_integer = randint(1, 100)


socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind((host_ip, port_number))

print("Socket created listening on port 80 ...")

while True:
    socket.listen(1)
    sock, addr = socket.accept()

    data = sock.recv(16384)
    text = data.decode('utf-8')
    client_name, number = text.split(" ")
    number = int(number)
    if (number > 100 or number < 1):
        print("Integer out-of-range, Server Shutting Down ...")
        socket.close()
        break
    else:
        print("----------------------------------------------------------")
        print("Client Name:", client_name, "Server Name:", server_name)
        print("CLient Number:", number, "Server Number:",
              random_integer, "Sum:", number+random_integer)
        message = f'{server_name} {random_integer}'
        sock.send(message.encode())
