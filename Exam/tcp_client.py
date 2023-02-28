import socket
from random import randint
from time import sleep

# Initialize host, port, buffer
host = "locahost"
port = 2833
buffer = 2048

# Server Info
server_host = "localhost"
server_port = 2832

# Object of socket class of type TCP
TCP_client_socket = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM)

# Connect to server
TCP_client_socket.connect((server_host, server_port))

print("TCP Connection estabilished with the server")
while True:
    random_arr = [randint(30, 90) for _ in range(7)]
    random_strs = [str(x) for x in random_arr]
    message = ' '.join(random_strs)
    TCP_client_socket.send(message.encode())

    # Wait for the message
    response = TCP_client_socket.recv(buffer)
    print(f"Sum: {response.decode()}")
    sleep(1)

