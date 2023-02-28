import socket
from time import sleep
from random import randint


# Define Host, Port and buffer
host = "localhost"
port = 2833
buffer = 2048


# Server Adderess
server_host = "localhost"
server_port = 2832

# Define object of socket class
UDP_client_socket = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)


# Bind host and port
UDP_client_socket.bind((host, port))

print("UDP client setup complete...")
while True:
    nums = [randint(30, 90) for i in range(7)]
    nums_str = [str(x) for x in nums]
    message = ' '.join(nums_str)
    UDP_client_socket.sendto(message.encode(), (server_host, server_port))
    
    # Wait for response
    message, address = UDP_client_socket.recvfrom(buffer)
    print(f"Sum: {message.decode()}, Address: {address}")
    sleep(2)




